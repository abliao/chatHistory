import os
import re
import imaplib
import email
import time
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import decode_header
from dotenv import load_dotenv
from openai import OpenAI
import prompt

# 加载环境变量
load_dotenv()

# 邮箱配置
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('EMAIL_PASSWORD')
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

# OpenAI配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

# 监听配置
SENDER_FILTER = os.getenv('SENDER_FILTER')  # 发件人邮箱
SUBJECT_KEYWORDS = os.getenv('SUBJECT_KEYWORDS', '').split(',')  # 标题关键词，用逗号分隔

def decode_email_header(header):
    """解码邮件标题"""
    decoded_header = decode_header(header)
    return ''.join([
        text.decode(charset or 'utf-8') if isinstance(text, bytes) else text
        for text, charset in decoded_header
    ])

def decode_email_content(text):
    """解读邮件内容"""
    pattern = r"(.*?)—————.*?—————\s*(.*)"
    match = re.search(pattern, text, re.S)

    # 提取分割结果
    before_time = match.group(1).strip() if match else "未找到分隔线前的内容"
    after_time = match.group(2).strip() if match else "未找到分隔线后的内容"
    return before_time, after_time
def get_email_content(msg):
    """获取邮件内容"""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()

def generate_response(subject,content):
    """生成回复"""
    body,history = decode_email_content(content)
    content = f"主题: {subject}\n聊天消息：\n{history}"
    print(f"content: {content}")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{prompt.reply_prompt}"},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API调用错误: {e}")
        return None

def send_email(to_address, subject, content):
    """发送邮件"""
    try:
        msg = MIMEText(content)
        msg['Subject'] = f"Re: {subject}"
        msg['From'] = EMAIL
        msg['To'] = to_address

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        print(f"回复邮件已发送至 {to_address}")
    except Exception as e:
        print(f"发送邮件失败: {e}")

def check_email():
    """检查邮件"""
    try:
        # 连接IMAP服务器
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select('INBOX')

        # 搜索未读邮件
        # 获取10分钟前的时间戳
        ten_minutes_ago = (datetime.now() - timedelta(minutes=10)).strftime("%d-%b-%Y")
        search_criteria = f'(UNSEEN SINCE "{ten_minutes_ago}")'
        _, messages = mail.search(None, search_criteria)
        for num in messages[0].split():
            _, msg_data = mail.fetch(num, '(RFC822)')
            email_body = msg_data[0][1]
            msg = email.message_from_bytes(email_body)
            
            # 获取发件人和主题
            from_address = msg['from']
            subject = decode_email_header(msg['subject'])
            
            # 检查是否符合过滤条件
            if SENDER_FILTER and SENDER_FILTER not in from_address:
                continue
                
            if SUBJECT_KEYWORDS and not any(keyword in subject for keyword in SUBJECT_KEYWORDS):
                continue
            
            # 获取邮件内容
            content = get_email_content(msg)
            if not content:
                continue
                
            print(f"收到符合条件的邮件:\n发件人: {from_address}\n主题: {subject}")
            print('内容\n',content)
            # 生成回复
            response = generate_response(subject,content)
            if response:
                # 发送回复
                sender_email = email.utils.parseaddr(from_address)[1]
                send_email(sender_email, subject, response)
                # 将邮件标记为已读
                mail.store(num, '+FLAGS', '\\Seen')
        mail.logout()
    except Exception as e:
        print(f"处理邮件时出错: {e}")

def main():
    print("邮件监听程序已启动...")
    while True:
        check_email()
        time.sleep(1) 

if __name__ == "__main__":
    main() 