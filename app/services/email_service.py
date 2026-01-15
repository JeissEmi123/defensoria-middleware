"""
Servicio para envío de emails usando la API de Gmail con Service Account o OAuth.
"""
import base64
import logging
import os
import pickle
from email.mime.text import MIMEText
from typing import Optional

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class EmailService:
    """Cliente que delega envíos de correo a Gmail a través de Service Account o OAuth."""

    def __init__(self):
        self.from_email = os.getenv("EMAIL_FROM", "noreply@defensoria.gob")
        self.gmail_service = None
        
        # Determinar método de autenticación
        use_oauth = os.getenv("GMAIL_USE_OAUTH", "false").lower() == "true"
        
        if use_oauth:
            self._init_oauth()
        else:
            self._init_service_account()

    def _init_oauth(self):
        """Inicializar con OAuth (Gmail personal)."""
        token_file = os.getenv("GMAIL_TOKEN_FILE", "config/gmail-token.pickle")

        if not os.path.exists(token_file):
            logger.warning("Token OAuth no encontrado en %s", token_file)
            return
        
        try:
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        with open(token_file, 'wb') as refreshed:
                            pickle.dump(creds, refreshed)
                        logger.info("Token OAuth refrescado correctamente")
                    except Exception as exc:
                        logger.warning("No se pudo refrescar el token OAuth: %s", exc)
                        return
                else:
                    logger.warning("Token OAuth inválido o expirado")
                    return
            
            self.gmail_service = build(
                "gmail",
                "v1",
                credentials=creds,
                cache_discovery=False
            )
            logger.info("Gmail API inicializado con OAuth")
            
        except Exception as exc:
            logger.error("Error inicializando OAuth: %s", exc)

    def _init_service_account(self):
        """Inicializar con Service Account (Google Workspace)."""
        service_account_file = os.getenv("GMAIL_SERVICE_ACCOUNT_FILE")
        delegated_user = os.getenv("GMAIL_DELEGATED_USER")

        if service_account_file and delegated_user:
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_file,
                    scopes=[
                        "https://www.googleapis.com/auth/gmail.send",
                        "https://www.googleapis.com/auth/gmail.readonly"
                    ]
                ).with_subject(delegated_user)
                self.gmail_service = build(
                    "gmail",
                    "v1",
                    credentials=credentials,
                    cache_discovery=False
                )
                logger.info("Gmail API inicializado con Service Account")
            except Exception as exc:
                logger.error("No se pudo inicializar el cliente Gmail API: %s", exc)
        else:
            if not service_account_file:
                logger.warning("GMAIL_SERVICE_ACCOUNT_FILE no configurado; no se enviarán correos.")
            if not delegated_user:
                logger.warning("GMAIL_DELEGATED_USER no configurado; no se enviarán correos.")

    def _crear_mensaje_html(self, to_email: str, subject: str, html_content: str) -> dict:
        mensaje = MIMEText(html_content, "html", "utf-8")
        mensaje["to"] = to_email
        mensaje["from"] = self.from_email
        mensaje["subject"] = subject
        return {"raw": base64.urlsafe_b64encode(mensaje.as_bytes()).decode()}

    def _enviar_html(self, to_email: str, subject: str, html_content: str) -> bool:
        if not self.gmail_service:
            logger.warning("Correo no enviado a %s porque el cliente Gmail no está listo.", to_email)
            return False

        mensaje = self._crear_mensaje_html(to_email, subject, html_content)
        try:
            self.gmail_service.users().messages().send(userId="me", body=mensaje).execute()
            logger.info("Correo enviado a %s vía Gmail API", to_email)
            return True
        except HttpError as err:
            logger.error("Error HTTP al enviar email a %s: %s", to_email, err)
            return False
        except Exception as exc:
            logger.error("Error al enviar email a %s: %s", to_email, exc)
            return False

    def send_welcome_email(
        self,
        to_email: str,
        username: str,
        temporary_password: str,
        nombre_completo: Optional[str] = None
    ) -> bool:
        """
        Envía un correo de bienvenida al usuario creado usando Gmail API.
        """
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
                <p>Si tienes alguna pregunta, contacta al administrador del sistema.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">Este es un mensaje automático, por favor no respondas.</p>
            </div>
        </body>
        </html>
        """
        return self._enviar_html(to_email, subject, html_content)

    def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_token: str
    ) -> bool:
        """
        Envía un correo con el enlace de recuperación de contraseña.
        """
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
                       style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Restablecer Contraseña
                    </a>
                </div>
                <p style="font-size: 14px; color: #666;">O copia y pega este enlace en tu navegador:<br>
                    <a href="{reset_url}">{reset_url}</a>
                </p>
                <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <p style="margin: 0;"><strong>⚠️ Este enlace expira en 1 hora</strong></p>
                </div>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">Defensoría del Pueblo - Sistema de Gestión</p>
            </div>
        </body>
        </html>
        """
        return self._enviar_html(to_email, subject, html_content)

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
        """
        Notifica al coordinador cuando se confirma un cambio de tipo de señal.
        """
        if not categoria_previa and not categoria_nueva:
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
        return self._enviar_html(to_email, subject, html_content)


# Instancia global
email_service = EmailService()
