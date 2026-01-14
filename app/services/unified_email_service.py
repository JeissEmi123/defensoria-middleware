"""
Servicio de email unificado que soporta múltiples proveedores.
"""
import logging
import os
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


class EmailProvider(ABC):
    """Interface base para proveedores de email."""
    
    @abstractmethod
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Enviar email."""
        pass


class SMTPProvider(EmailProvider):
    """Proveedor SMTP genérico."""
    
    def __init__(self):
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("EMAIL_FROM", self.username)
        
        if not all([self.host, self.username, self.password]):
            logger.warning("Configuración SMTP incompleta")
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Enviar email via SMTP."""
        if not all([self.host, self.username, self.password]):
            logger.warning("SMTP no configurado correctamente")
            return False
        
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Enviar
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email SMTP enviado a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email SMTP: {e}")
            return False


class SendGridProvider(EmailProvider):
    """Proveedor SendGrid."""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("EMAIL_FROM")
        
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY no configurado")
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Enviar email via SendGrid."""
        if not self.api_key:
            logger.warning("SendGrid no configurado")
            return False
        
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            response = sg.send(message)
            logger.info(f"Email SendGrid enviado a {to_email}. Status: {response.status_code}")
            return response.status_code == 202
            
        except ImportError:
            logger.error("SendGrid no instalado. Instalar con: pip install sendgrid")
            return False
        except Exception as e:
            logger.error(f"Error enviando email SendGrid: {e}")
            return False


class UnifiedEmailService:
    """Servicio de email unificado."""
    
    def __init__(self):
        self.provider = self._get_provider()
    
    def _get_provider(self) -> Optional[EmailProvider]:
        """Seleccionar proveedor basado en configuración."""
        email_service = os.getenv("EMAIL_SERVICE", "gmail").lower()
        
        if email_service == "sendgrid":
            return SendGridProvider()
        elif email_service == "smtp":
            return SMTPProvider()
        elif email_service == "gmail":
            # Fallback al servicio Gmail existente
            from app.services.email_service import EmailService as GmailService
            gmail_service = GmailService()
            
            class GmailAdapter(EmailProvider):
                def __init__(self, gmail_svc):
                    self.gmail_svc = gmail_svc
                
                def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
                    return self.gmail_svc._enviar_html(to_email, subject, html_content)
            
            return GmailAdapter(gmail_service)
        else:
            logger.error(f"Proveedor de email desconocido: {email_service}")
            return None
    
    def send_welcome_email(self, to_email: str, username: str, temporary_password: str, nombre_completo: Optional[str] = None) -> bool:
        """Enviar email de bienvenida."""
        if not self.provider:
            return False
        
        subject = "Bienvenido a Defensoría del Pueblo"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">¡Bienvenido a Defensoría del Pueblo!</h2>
                <p>Hola {nombre_completo or username},</p>
                <p>Tu cuenta ha sido creada exitosamente. A continuación encontrarás tus credenciales:</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Usuario:</strong> {username}</p>
                    <p style="margin: 5px 0;"><strong>Contraseña temporal:</strong> {temporary_password}</p>
                </div>
                <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <p style="margin: 0;"><strong>⚠️ Importante:</strong></p>
                    <p style="margin: 5px 0;">Por seguridad, debes cambiar tu contraseña en el primer inicio de sesión.</p>
                </div>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">Este es un mensaje automático, por favor no respondas.</p>
            </div>
        </body>
        </html>
        """
        return self.provider.send_email(to_email, subject, html_content)
    
    def send_password_reset_email(self, to_email: str, username: str, reset_token: str) -> bool:
        """Enviar email de reset de contraseña."""
        if not self.provider:
            return False
        
        reset_url = f"https://tu-frontend.com/reset-password?token={reset_token}"
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
                       style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Restablecer Contraseña
                    </a>
                </div>
                <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <p style="margin: 0;"><strong>⚠️ Este enlace expira en 1 hora</strong></p>
                </div>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">Defensoría del Pueblo - Sistema de Gestión</p>
            </div>
        </body>
        </html>
        """
        return self.provider.send_email(to_email, subject, html_content)
    
    def send_signal_revision_notification(
        self,
        to_email: str,
        senal_id: int,
        categoria_previa: Optional[str],
        categoria_nueva: Optional[str],
        usuario: Optional[str],
        confirmo_revision: Optional[bool],
        fecha_actualizacion: Optional[str],
        detalles: Optional[str] = None
    ) -> bool:
        """Notificación de cambio de señal."""
        if not self.provider or not categoria_previa and not categoria_nueva:
            return False

        confirmo_text = "Sí" if confirmo_revision else "No"
        subject = f"Cambio confirmado en tipo de señal #{senal_id}"
        fecha_info = f"<p><strong>Fecha de actualización:</strong> {fecha_actualizacion}</p>" if fecha_actualizacion else ""
        detalles_text = f"<p>{detalles}</p>" if detalles else ""

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Cambio validado en el tipo de señal</h2>
                <p>Se ha confirmado un cambio de categoría para la señal <strong>#{senal_id}</strong>.</p>
                <p><strong>Revisor:</strong> {usuario or "Sistema"}</p>
                <p><strong>Tipo anterior:</strong> {categoria_previa or "No registrado"}</p>
                <p><strong>Tipo actual:</strong> {categoria_nueva or "No registrado"}</p>
                <p><strong>Confirmó revisión:</strong> {confirmo_text}</p>
                {fecha_info}
                {detalles_text}
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">
                    Este es un mensaje automático generado desde el middleware de Defensoría del Pueblo.
                </p>
            </div>
        </body>
        </html>
        """
        return self.provider.send_email(to_email, subject, html_content)


# Instancia global
unified_email_service = UnifiedEmailService()