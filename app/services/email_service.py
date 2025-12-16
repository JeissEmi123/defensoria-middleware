"""
Servicio de envío de emails usando SendGrid
"""
import os
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para envío de emails"""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("EMAIL_FROM", "noreply@defensoria.gob")
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None
        
        if not self.client:
            logger.warning("SendGrid API Key no configurada. Emails deshabilitados.")
    
    def send_welcome_email(
        self,
        to_email: str,
        username: str,
        temporary_password: str,
        nombre_completo: Optional[str] = None
    ) -> bool:
        """
        Envía email de bienvenida a usuario nuevo
        
        Args:
            to_email: Email del destinatario
            username: Nombre de usuario
            temporary_password: Contraseña temporal
            nombre_completo: Nombre completo del usuario
            
        Returns:
            bool: True si se envió correctamente
        """
        if not self.client:
            logger.warning(f"Email no enviado a {to_email} - SendGrid no configurado")
            return False
        
        try:
            # Construir mensaje
            subject = "Bienvenido a Defensoría del Pueblo"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">¡Bienvenido a Defensoría del Pueblo!</h2>
                    
                    <p>Hola {nombre_completo or username},</p>
                    
                    <p>Tu cuenta ha sido creada exitosamente. A continuación encontrarás tus credenciales de acceso:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 5px 0;"><strong>Usuario:</strong> {username}</p>
                        <p style="margin: 5px 0;"><strong>Contraseña temporal:</strong> {temporary_password}</p>
                        <p style="margin: 5px 0;"><strong>URL de acceso:</strong> <a href="https://defensoria-frontend-411798681660.us-central1.run.app">Ir al sistema</a></p>
                    </div>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <p style="margin: 0;"><strong>⚠️ Importante:</strong></p>
                        <p style="margin: 5px 0;">Por seguridad, debes cambiar tu contraseña en el primer inicio de sesión.</p>
                    </div>
                    
                    <h3 style="color: #2c3e50;">Primeros pasos:</h3>
                    <ol>
                        <li>Accede al sistema usando el enlace de arriba</li>
                        <li>Inicia sesión con tus credenciales</li>
                        <li>Cambia tu contraseña temporal</li>
                        <li>Completa tu perfil</li>
                    </ol>
                    
                    <p>Si tienes alguna pregunta o necesitas ayuda, no dudes en contactar al administrador del sistema.</p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #666;">
                        Este es un mensaje automático, por favor no respondas a este correo.<br>
                        Defensoría del Pueblo - Sistema de Gestión
                    </p>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            # Enviar
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email enviado exitosamente a {to_email}")
                return True
            else:
                logger.error(f"Error al enviar email: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error al enviar email a {to_email}: {str(e)}")
            return False
    
    def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_token: str
    ) -> bool:
        """
        Envía email de recuperación de contraseña
        
        Args:
            to_email: Email del destinatario
            username: Nombre de usuario
            reset_token: Token de recuperación
            
        Returns:
            bool: True si se envió correctamente
        """
        if not self.client:
            logger.warning(f"Email no enviado a {to_email} - SendGrid no configurado")
            return False
        
        try:
            reset_url = f"https://defensoria-frontend-411798681660.us-central1.run.app/reset-password?token={reset_token}"
            
            subject = "Recuperación de Contraseña - Defensoría del Pueblo"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Recuperación de Contraseña</h2>
                    
                    <p>Hola {username},</p>
                    
                    <p>Recibimos una solicitud para restablecer tu contraseña. Si no fuiste tú, ignora este mensaje.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" 
                           style="background-color: #007bff; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Restablecer Contraseña
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666;">
                        O copia y pega este enlace en tu navegador:<br>
                        <a href="{reset_url}">{reset_url}</a>
                    </p>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <p style="margin: 0;"><strong>⚠️ Este enlace expira en 1 hora</strong></p>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #666;">
                        Defensoría del Pueblo - Sistema de Gestión
                    </p>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email de recuperación enviado a {to_email}")
                return True
            else:
                logger.error(f"Error al enviar email: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error al enviar email a {to_email}: {str(e)}")
            return False


# Instancia global
email_service = EmailService()
