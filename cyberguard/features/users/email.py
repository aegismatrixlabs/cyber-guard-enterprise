import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cyberguard.core.config import settings

def send_reset_email(to_email: str, token: str):
    subject = "AEGISMATRIX - Şifre Sıfırlama Talebi"
    reset_link = f"http://localhost:5000/reset-password?token={token}"
    
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0f111a; color: #e2e8f0; padding: 20px;">
        <h2 style="color: #00ff88;">AEGISMATRIX CyberGuard</h2>
        <p>Şifre sıfırlama talebinde bulundunuz. Aşağıdaki linke tıklayarak yeni şifrenizi belirleyebilirsiniz.</p>
        <p><a href="{reset_link}" style="background-color: #00c853; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Şifremi Sıfırla</a></p>
        <p style="font-size: 0.8em; color: #8b92b6;">Bu link 15 dakika boyunca geçerlidir.</p>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
        server.sendmail(settings.EMAIL_USER, to_email, msg.as_string())
        server.quit()
        print(f"✅ Şifre sıfırlama maili başarıyla gönderildi: {to_email}")
        return True
    except Exception as e:
        print(f"❌ Mail gönderim hatası: {e}")
        return False
