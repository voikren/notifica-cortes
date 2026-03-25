import msal
import requests
import base64
from config.settings import settings


def _obtener_token() -> str:
    """Obtiene el token de acceso via Client Credentials con Azure AD."""
    app = msal.ConfidentialClientApplication(
        client_id=settings.CLIENT_ID,
        client_credential=settings.CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{settings.TENANT_ID}"
    )

    resultado = app.acquire_token_by_username_password(
        username=settings.USUARIO,
        password=settings.PASSWORD,
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" not in resultado:
        error = resultado.get("error_description", "Error desconocido")
        raise RuntimeError(f"Error obteniendo token: {error}")

    return resultado["access_token"]


def enviar_correo(destinatario: str, cc: str, html: str):
    """Envía el correo HTML via Microsoft Graph API."""
    token = _obtener_token()

    mensaje = {
        "message": {
            "subject": "Notificacion de Faltantes",
            "body": {
                "contentType": "HTML",
                "content": html
            },
            "toRecipients": [
                {"emailAddress": {"address": destinatario}}
            ],
            "ccRecipients": [
                {"emailAddress": {"address": cc}}
            ]
        },
        "saveToSentItems": "true"
    }

    respuesta = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{settings.USUARIO}/sendMail",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=mensaje
    )

    if respuesta.status_code == 202:
        print(f"[OK] Correo enviado a {destinatario} (CC: {cc})")
    else:
        raise RuntimeError(f"Error enviando correo: {respuesta.status_code} - {respuesta.text}")