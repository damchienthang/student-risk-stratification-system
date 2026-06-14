import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.core.config import settings

def send_warning_email(to_email: str, student_id: str, recommendation: str, risk_label: str) -> bool:
    """
    Gửi email cảnh báo rủi ro học tập tới sinh viên/phụ huynh.
    """
    sender_email = settings.SMTP_EMAIL
    sender_password = settings.SMTP_PASSWORD

    if not sender_email or not sender_password:
        print("Lỗi: Chưa cấu hình SMTP_EMAIL hoặc SMTP_PASSWORD trong .env")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Khẩn cấp] Cảnh báo rủi ro học tập - Sinh viên #{student_id}"
    msg["From"] = f"Hệ thống Cố vấn Học tập <{sender_email}>"
    msg["To"] = to_email

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #c92a2a;">Cảnh báo Rủi ro Học tập</h2>
        <p>Chào em (Sinh viên mã số <b>#{student_id}</b>),</p>
        <p>Hệ thống đánh giá rủi ro học tập vừa phân tích dữ liệu tương tác học tập của em và nhận thấy em đang ở nhóm rủi ro: <strong style="color: red;">{risk_label}</strong>.</p>
        <p>Dưới đây là khuyến nghị từ Cố vấn học tập:</p>
        <div style="background-color: #fff5f5; border-left: 4px solid #c92a2a; padding: 10px 15px; margin: 15px 0;">
            <em>"{recommendation}"</em>
        </div>
        <p>Em vui lòng xem xét và làm theo khuyến nghị trên. Nếu cần hỗ trợ, hãy liên hệ ngay với giảng viên bộ môn hoặc cố vấn học tập để được tư vấn.</p>
        <br/>
        <p>Trân trọng,<br/><b>Ban Cố vấn Học tập - Hệ thống RiskSight</b></p>
      </body>
    </html>
    """

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")
        return False
