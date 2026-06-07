# ElectroBot

ElectroBot is a full-stack Flask chatbot project with:

- Login page using mail ID and password
- Login notification email to the entered mail ID
- Electronics-only chatbot
- Alert message for unrelated topics
- OpenAI-powered electronics answers when `OPENAI_API_KEY` is configured
- Responsive frontend with a clean dashboard-style interface

## Run the Project

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python CHATBOT.py
```

Open:

```text
http://127.0.0.1:5000
```

## Enable Email Sending

Email is intentionally configured through environment variables so passwords are not saved in code.

1. Copy `.env.example` values into your system environment, or set them in PowerShell.
2. For Gmail, create an App Password from your Google Account security settings.
3. Start the Flask app after setting the variables.

PowerShell example:

```powershell
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USERNAME="your-email@gmail.com"
$env:SMTP_PASSWORD="your-app-password"
$env:SMTP_FROM="your-email@gmail.com"
python CHATBOT.py
```

If SMTP variables are not configured, login still works and the app shows a warning that email was not sent.

## Enable OpenAI Answers

Set your OpenAI key as an environment variable before running the app. Do not paste the key into Python, HTML, CSS, or JavaScript files.

```powershell
$env:OPENAI_API_KEY="your-new-openai-api-key"
$env:OPENAI_MODEL="gpt-5.4-mini"
python CHATBOT.py
```

If `OPENAI_API_KEY` is missing or the API call fails, the app uses the built-in electronics helper instead.


<img width="1598" height="841" alt="image" src="https://github.com/user-attachments/assets/2fd3b57a-7fce-4d3c-a0f3-2431b723fd0e" />
<img width="1886" height="913" alt="image" src="https://github.com/user-attachments/assets/cbf77960-23ad-449c-937b-b15db6933631" />


