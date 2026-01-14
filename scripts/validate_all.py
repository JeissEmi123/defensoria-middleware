#!/usr/bin/env python3
"""
Script maestro para validar toda la configuración GCP/Gmail
Ejecuta todos los tests de validación en secuencia
"""
import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

def run_script(script_path, description):
    """Ejecutar un script de validación"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              cwd=Path(__file__).parent.parent,
                              timeout=120)
        success = result.returncode == 0
        
        if success:
            print(f"\n✅ {description} - COMPLETADO")
        else:
            print(f"\n❌ {description} - FALLÓ")
        
        return success
        
    except subprocess.TimeoutExpired:
        print(f"\n⏰ {description} - TIMEOUT (más de 2 minutos)")
        return False
    except Exception as e:
        print(f"\n❌ {description} - ERROR: {e}")
        return False

def check_dependencies():
    """Verificar dependencias necesarias"""
    print("🔍 Verificando dependencias...")
    
    missing_deps = []
    
    # Verificar Python packages
    try:
        import requests
        print("✅ requests - OK")
    except ImportError:
        missing_deps.append("requests")
        print("❌ requests - FALTANTE")
    
    try:
        import aiohttp
        print("✅ aiohttp - OK")
    except ImportError:
        missing_deps.append("aiohttp")
        print("❌ aiohttp - FALTANTE")
    
    if missing_deps:
        print("\n⚠️  Dependencias faltantes. Instala con:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    return True

def check_environment():
    """Verificar entorno básico"""
    print("\n🔍 Verificando entorno...")
    
    # Verificar que existe el .env
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Archivo .env encontrado")
    else:
        print("❌ Archivo .env no encontrado")
        return False
    
    # Verificar estructura del proyecto
    required_dirs = ["app", "scripts", "docs"]
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ Directorio {dir_name} - OK")
        else:
            print(f"❌ Directorio {dir_name} - FALTANTE")
            return False
    
    return True

def main():
    """Función principal que ejecuta todos los tests"""
    print("🚀 VALIDACIÓN COMPLETA DEL SISTEMA GCP/GMAIL")
    print("Defensoría del Pueblo - Sistema de Señales")
    print("=" * 60)
    
    # 1. Verificar entorno
    if not check_environment():
        print("❌ Problemas en el entorno básico")
        return False
    
    # 2. Verificar dependencias
    if not check_dependencies():
        print("❌ Dependencias faltantes")
        return False
    
    scripts_dir = Path(__file__).parent
    results = {}
    
    # 3. Diagnóstico de conectividad
    results["Conectividad GCP"] = run_script(
        scripts_dir / "diagnose_gcp_connectivity.py",
        "DIAGNÓSTICO DE CONECTIVIDAD"
    )
    
    # 4. Validación de configuración
    results["Configuración Gmail"] = run_script(
        scripts_dir / "validate_gcp_config.py", 
        "VALIDACIÓN DE CONFIGURACIÓN GMAIL"
    )
    
    # 5. Test del flujo completo (solo si la configuración está OK)
    if results["Configuración Gmail"]:
        print("\n🤔 ¿Quieres probar el flujo completo de envío de emails?")
        print("   Esto creará una señal de prueba y enviará un email real")
        
        response = input("   Continuar? (s/N): ").lower().strip()
        
        if response in ['s', 'si', 'sí', 'yes', 'y']:
            results["Flujo Completo"] = run_script(
                scripts_dir / "test_email_flow.py",
                "TEST COMPLETO DEL FLUJO DE EMAIL"
            )
        else:
            print("⏭️  Saltando test de flujo completo")
            results["Flujo Completo"] = None
    else:
        print("⏭️  Saltando test de flujo completo - configuración incorrecta")
        results["Flujo Completo"] = None
    
    # 6. Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN FINAL")
    print('='*60)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, result in results.items():
        if result is not None:
            total_tests += 1
            if result:
                passed_tests += 1
                print(f"✅ {test_name}")
            else:
                print(f"❌ {test_name}")
        else:
            print(f"⏭️  {test_name} - SALTADO")
    
    print(f"\nResultado: {passed_tests}/{total_tests} tests pasaron")
    
    if passed_tests == total_tests and total_tests > 0:
        print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("✅ Todo está configurado correctamente")
        print("📧 Los emails se enviarán automáticamente cuando se confirmen revisiones")
    elif passed_tests > 0:
        print("\n⚠️  CONFIGURACIÓN PARCIAL")
        print("🔧 Algunos componentes necesitan atención")
    else:
        print("\n❌ CONFIGURACIÓN INCORRECTA")
        print("🔧 Revisa la documentación en docs/CONFIGURACION_EMAIL.md")
    
    print(f"\n📚 Documentación adicional:")
    print(f"   - docs/CONFIGURACION_EMAIL.md")
    print(f"   - app/services/email_service.py")
    print(f"   - app/config.py")
    
    return passed_tests == total_tests and total_tests > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Validación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)