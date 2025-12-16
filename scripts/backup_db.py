import asyncio
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
import gzip
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


class PostgreSQLBackup:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Parsear DATABASE_URL
        # postgresql+asyncpg://user:pass@host:port/dbname
        db_url = settings.database_url.replace("postgresql+asyncpg://", "")
        
        if "@" in db_url:
            auth, location = db_url.split("@")
            self.user, self.password = auth.split(":")
            host_port, self.dbname = location.split("/")
            
            if ":" in host_port:
                self.host, port = host_port.split(":")
                self.port = int(port)
            else:
                self.host = host_port
                self.port = 5432
        else:
            raise ValueError("DATABASE_URL no válida")
    
    def crear_backup(self, comprimir=True):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.sql"
        
        logger.info("iniciando_backup", file=str(backup_file))
        print(f"\n Creando backup: {backup_file}")
        
        # Configurar variables de entorno
        env = os.environ.copy()
        env['PGPASSWORD'] = self.password
        
        try:
            # Ejecutar pg_dump
            cmd = [
                "pg_dump",
                "-h", self.host,
                "-p", str(self.port),
                "-U", self.user,
                "-d", self.dbname,
                "-F", "p",  # Plain text format
                "-f", str(backup_file),
                "--verbose",
                "--clean",  # Include DROP statements
                "--if-exists",  # Use IF EXISTS with DROP
                "--no-owner",  # Don't output ownership commands
                "--no-privileges"  # Don't output privilege commands
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("backup_creado", file=str(backup_file))
            print(f" Backup creado: {backup_file}")
            
            # Comprimir si se solicita
            if comprimir:
                print(f"  Comprimiendo backup...")
                compressed_file = Path(str(backup_file) + ".gz")
                
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Eliminar archivo sin comprimir
                backup_file.unlink()
                
                size_mb = compressed_file.stat().st_size / (1024 * 1024)
                logger.info("backup_comprimido", file=str(compressed_file), size_mb=round(size_mb, 2))
                print(f" Backup comprimido: {compressed_file} ({size_mb:.2f} MB)")
                
                return compressed_file
            
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            print(f" Tamaño: {size_mb:.2f} MB")
            return backup_file
            
        except subprocess.CalledProcessError as e:
            logger.error("error_backup", error=str(e), stderr=e.stderr)
            print(f" Error en backup: {e.stderr}")
            raise
        except Exception as e:
            logger.error("error_backup", error=str(e))
            print(f" Error: {str(e)}")
            raise
    
    def restaurar_backup(self, backup_file: Path):
        logger.info("iniciando_restauracion", file=str(backup_file))
        print(f"\n Restaurando backup: {backup_file}")
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {backup_file}")
        
        # Descomprimir si es necesario
        if backup_file.suffix == ".gz":
            print(" Descomprimiendo backup...")
            sql_file = Path(str(backup_file).replace(".gz", ""))
            
            with gzip.open(backup_file, 'rb') as f_in:
                with open(sql_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            backup_file = sql_file
        
        # Configurar variables de entorno
        env = os.environ.copy()
        env['PGPASSWORD'] = self.password
        
        try:
            # Ejecutar psql
            cmd = [
                "psql",
                "-h", self.host,
                "-p", str(self.port),
                "-U", self.user,
                "-d", self.dbname,
                "-f", str(backup_file),
                "--single-transaction"  # Todo en una transacción
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("restauracion_completada")
            print(" Restauración completada exitosamente")
            
            # Limpiar archivo temporal si fue descomprimido
            if backup_file.suffix == ".sql" and not backup_file.parent.name.endswith(".gz"):
                backup_file.unlink()
            
        except subprocess.CalledProcessError as e:
            logger.error("error_restauracion", error=str(e), stderr=e.stderr)
            print(f" Error en restauración: {e.stderr}")
            raise
        except Exception as e:
            logger.error("error_restauracion", error=str(e))
            print(f" Error: {str(e)}")
            raise
    
    def listar_backups(self):
        backups = sorted(
            self.backup_dir.glob("backup_*.sql*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if not backups:
            print("\n  No hay backups disponibles")
            return []
        
        print("\n" + "="*80)
        print(" BACKUPS DISPONIBLES")
        print("="*80)
        print(f"{'#':<4} {'Archivo':<40} {'Fecha':<20} {'Tamaño':<10}")
        print("-"*80)
        
        for idx, backup in enumerate(backups, 1):
            size_mb = backup.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"{idx:<4} {backup.name:<40} {mtime.strftime('%Y-%m-%d %H:%M:%S'):<20} {size_mb:>8.2f} MB")
        
        print("="*80 + "\n")
        return backups
    
    def eliminar_backups_antiguos(self, dias=30):
        logger.info("eliminando_backups_antiguos", dias=dias)
        print(f"\n  Eliminando backups con más de {dias} días...")
        
        limite = datetime.now().timestamp() - (dias * 24 * 60 * 60)
        eliminados = 0
        
        for backup in self.backup_dir.glob("backup_*.sql*"):
            if backup.stat().st_mtime < limite:
                backup.unlink()
                eliminados += 1
                logger.info("backup_eliminado", file=backup.name)
        
        print(f" {eliminados} backup(s) eliminado(s)")


def main():
    backup_manager = PostgreSQLBackup()
    print("\n" + "="*80)
    print("  GESTIÓN DE BACKUPS - PostgreSQL")
    print("="*80)
    print("\n1. Crear backup")
    print("2. Restaurar backup")
    print("3. Listar backups")
    print("4. Eliminar backups antiguos")
    print("5. Crear backup automático (comprimido)")
    print("0. Salir\n")
    
    opcion = input("Seleccione una opción: ")
    
    try:
        if opcion == "1":
            comprimir = input("\n¿Comprimir backup? (s/n): ").lower() == 's'
            backup_manager.crear_backup(comprimir=comprimir)
            
        elif opcion == "2":
            backups = backup_manager.listar_backups()
            if backups:
                idx = int(input("\nNúmero de backup a restaurar: ")) - 1
                if 0 <= idx < len(backups):
                    confirmacion = input(f"\n  ¿Confirmar restauración de '{backups[idx].name}'? (s/n): ")
                    if confirmacion.lower() == 's':
                        backup_manager.restaurar_backup(backups[idx])
                else:
                    print(" Número inválido")
        
        elif opcion == "3":
            backup_manager.listar_backups()
        
        elif opcion == "4":
            dias = int(input("\n¿Eliminar backups con más de cuántos días? (default: 30): ") or "30")
            confirmacion = input(f"  ¿Confirmar eliminación de backups > {dias} días? (s/n): ")
            if confirmacion.lower() == 's':
                backup_manager.eliminar_backups_antiguos(dias)
        
        elif opcion == "5":
            # Backup automático con compresión
            backup_file = backup_manager.crear_backup(comprimir=True)
            print(f"\n Backup automático completado: {backup_file}")
        
        elif opcion == "0":
            print(" Saliendo...")
        
        else:
            print(" Opción inválida")
    
    except Exception as e:
        logger.error("error_gestion_backups", error=str(e))
        print(f"\n Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
