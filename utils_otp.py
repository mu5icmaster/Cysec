# utils_otp.py
import os, time, random, smtplib, ssl, bcrypt
from email.message import EmailMessage

OTP_TTL = 300          # 5 minutes
OTP_LEN = 6
MAX_ATTEMPTS = 3

def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"

def hash_otp(otp: str) -> bytes:
    return bcrypt.hashpw(otp.encode(), bcrypt.gensalt())

def check_otp(otp: str, code_hash: bytes) -> bool:
    try:
        return bcrypt.checkpw(otp.encode(), code_hash)
    except Exception:
        return False

def now() -> int:
    return int(time.time())

# 简易邮件发送（生产建议用应用专用密码）
def send_otp_email(to_email: str, otp: str):
    sender = "yenyang928@gmail.com"
    passwd = "wggsizdxwvdvezye"
    host   = "smtp.gmail.com"
    port   = 587

# send_otp_email 里，发送前加：
    print(f"[DEV] OTP for {to_email}: {otp}")   # 开发期总是打印一份


    if not (sender and passwd):
        print(f"[DEV] OTP for {to_email}: {otp}")  # 开发期用打印
        return

    msg = EmailMessage()
    msg["Subject"] = "Your KEAI WMS One-Time Password"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(f"Your one-time password is: {otp}\nIt expires in 5 minutes.")

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        server.login(sender, passwd)
        server.send_message(msg)
