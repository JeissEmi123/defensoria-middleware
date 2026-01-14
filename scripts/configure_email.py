#!/usr/bin/env python3
"""
Script maestro para configurar emails desde dominios genéricos.
Presenta todas las opciones disponibles.
"""

def show_options():
    """Mostrar opciones de configuración de email."""
    print("📧 Configurador de Email - Defensoría Middleware")
    print("=" * 60)
    print()
    print("Selecciona el método de envío de emails:")
    print()
    print("1️⃣  SMTP + Gmail Personal (App Password)")
    print("   ✅ Más simple y rápido")
    print("   ✅ Funciona con cualquier Gmail")
    print("   ⚠️  Requiere App Password (2FA habilitado)")
    print()
    print("2️⃣  OAuth + Gmail Personal")
    print("   ✅ Más seguro que SMTP")
    print("   ✅ No requiere contraseñas")
    print("   ⚠️  Configuración más compleja")
    print()
    print("3️⃣  SendGrid (Profesional)")
    print("   ✅ Ideal para producción")
    print("   ✅ Altas cuotas de envío")
    print("   ⚠️  Requiere cuenta SendGrid")
    print()
    print("4️⃣  Service Account (Ya configurado)")
    print("   ✅ Para Google Workspace")
    print("   ⚠️  Requiere dominio empresarial")
    print()
    print("5️⃣  Mostrar configuración actual")
    print()


def main():
    """Ejecutar configurador maestro."""
    show_options()
    
    try:
        choice = input("👉 Selecciona una opción (1-5): ").strip()
        
        if choice == "1":
            print("\n🔧 Configurando SMTP + Gmail Personal...")
            import subprocess
            subprocess.run(["/usr/local/bin/python3", "scripts/setup_smtp_gmail.py"])
            
        elif choice == "2":
            print("\n🔧 Configurando OAuth + Gmail Personal...")
            print("ℹ️  Primero necesitas instalar dependencias:")
            print("    pip install google-auth-oauthlib")
            install = input("¿Instalar ahora? (y/n): ").lower().strip()
            if install in ['y', 'yes', 'sí', 'si']:
                import subprocess
                subprocess.run(["/usr/local/bin/python3", "-m", "pip", "install", "google-auth-oauthlib"])
                subprocess.run(["/usr/local/bin/python3", "scripts/setup_oauth_gmail.py"])
            else:
                print("⚠️ Instala las dependencias y ejecuta: python scripts/setup_oauth_gmail.py")
                
        elif choice == "3":
            print("\n🔧 Configurando SendGrid...")
            print("ℹ️  Pasos para SendGrid:")
            print("1. Crear cuenta en https://sendgrid.com/")
            print("2. Obtener API Key")
            print("3. pip install sendgrid")
            print("4. Configurar variables de entorno:")
            print()
            api_key = input("SendGrid API Key: ").strip()
            from_email = input("Email remitente: ").strip()
            coordinator = input("Email coordinador: ").strip()
            
            config = f"""
# === CONFIGURACIÓN SENDGRID ===
EMAIL_SERVICE=sendgrid
SENDGRID_API_KEY={api_key}
EMAIL_FROM={from_email}
COORDINADOR_EMAIL={coordinator}
"""
            print("\n📝 Agregar al .env:")
            print(config)
            
        elif choice == "4":
            print("\n🏢 Service Account ya está configurado!")
            print("Para usar con dominio empresarial:")
            print("1. Configura Domain-wide Delegation")
            print("2. Usa email válido de tu dominio")
            print("3. Ver: docs/GMAIL_SETUP_FINAL.md")
            
        elif choice == "5":
            print("\n📊 Configuración actual:")
            import os
            configs = [
                ("EMAIL_SERVICE", "Servicio de email"),
                ("GMAIL_USE_OAUTH", "Usar OAuth Gmail"),
                ("SMTP_HOST", "Servidor SMTP"),
                ("SENDGRID_API_KEY", "SendGrid API"),
                ("EMAIL_FROM", "Email remitente"),
                ("COORDINADOR_EMAIL", "Email coordinador")
            ]
            
            for key, desc in configs:
                value = os.getenv(key, "❌ No configurado")
                if "API_KEY" in key or "PASSWORD" in key:
                    value = "[OCULTO]" if value != "❌ No configurado" else value
                print(f"   {desc}: {value}")
                
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print("\n\n👋 Configuración cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()