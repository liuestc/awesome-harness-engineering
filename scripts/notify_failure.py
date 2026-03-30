#!/usr/bin/env python3
"""Send failure notification email for GitHub Actions pipeline."""
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

smtp_user = os.environ.get("SMTP_USER", "")
smtp_pass = os.environ.get("SMTP_PASS", "")
notify_email = os.environ.get("NOTIFY_EMAIL", "")
smtp_host = os.environ.get("SMTP_HOST", "smtp.qq.com")
smtp_port = int(os.environ.get("SMTP_PORT", "587"))

if not all([smtp_user, smtp_pass, notify_email]):
    print("Email config incomplete, skipping notification")
    exit(0)

now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
body = (
    "Harness Engineering Pipeline 运行失败！\n\n"
    "时间: " + now_str + " UTC\n"
    "仓库: https://github.com/liuestc/awesome-harness-engineering\n"
    "Actions 日志: https://github.com/liuestc/awesome-harness-engineering/actions\n\n"
    "请检查 GitHub Actions 日志了解详情。"
)

msg = MIMEText(body, "plain", "utf-8")
msg["Subject"] = "⚠️ Harness Engineering Pipeline 运行失败"
msg["From"] = smtp_user
msg["To"] = notify_email

try:
    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.sendmail(smtp_user, notify_email, msg.as_string())
    print("Failure notification sent to " + notify_email)
except Exception as e:
    print("Failed to send notification: " + str(e))
