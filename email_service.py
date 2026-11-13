import os
import resend

resend.api_key = os.getenv('RESEND_API_KEY')

def send_reset_email(to_email: str, token: str):
    reset_url = f"http://localhost:8000/reset-password?token={token}"
    params = {
        "from": "onboarding@resend.dev",
        "to": [to_email],
        "subject": "Recuperare parolă - PostATodo",
        "html": f"""
            <p>Salut,</p>
            <p>Ai solicitat resetarea parolei pentru contul tău. Dă click pe linkul de mai jos pentru a continua:</p>
            <p><a href="{reset_url}">Resetează parola</a></p>
            <p>Dacă nu ai solicitat acest lucru, poți ignora acest email.</p>
        """
    }
    try:
        response = resend.Emails.send(params)
        print(f"Email trimis cu succes! Răspuns Resend: {response}")
    except Exception as e:
        print(f"Eroare la trimiterea emailului prin Resend: {e}")