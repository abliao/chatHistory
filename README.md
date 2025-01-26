# 邮件监听自动回复系统

这是一个自动监听邮件并使用 OpenAI API 生成回复的程序。

## 功能特点

- 监听指定邮箱的新邮件
- 根据发件人和邮件主题进行过滤
- 使用 OpenAI API 自动生成回复内容
- 自动发送回复邮件

## 安装步骤

1. 克隆项目到本地
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 复制 `.env.example` 文件并重命名为 `.env`
4. 在 `.env` 文件中配置你的环境变量：
   - 设置邮箱账号和密码
   - 配置 IMAP 和 SMTP 服务器信息
   - 添加 OpenAI API 密钥
   - 设置发件人过滤和主题关键词

## 使用说明

1. 确保已正确配置所有环境变量
2. 运行程序：
   ```bash
   python email_monitor.py
   ```
3. 程序将开始监听邮箱，每分钟检查一次新邮件

## 注意事项

- 如果使用 Gmail，需要开启"低安全性应用访问"或使用应用专用密码
- 确保 OpenAI API 密钥有足够的额度
- 建议先在测试环境中运行，确认配置正确后再用于生产环境

## 配置说明

在 `.env` 文件中：

- `EMAIL`: 你的邮箱地址
- `EMAIL_PASSWORD`: 邮箱密码或应用专用密码
- `IMAP_SERVER`: IMAP 服务器地址
- `SMTP_SERVER`: SMTP 服务器地址
- `SMTP_PORT`: SMTP 服务器端口
- `OPENAI_API_KEY`: OpenAI API 密钥
- `SENDER_FILTER`: 发件人邮箱过滤（可选）
- `SUBJECT_KEYWORDS`: 主题关键词过滤，用逗号分隔（可选） 