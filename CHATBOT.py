import os
import re
import smtplib
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv
from functools import wraps

# Load environment variables from a local .env file if present
load_dotenv()

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from groq import Groq


app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "8f7d2c9a4b1e6f3d8a5c7e9f1b2d4a6c"
)

ELECTRONICS_KEYWORDS = {
    "adapter",
    "android",
    "appliance",
    "battery",
    "bluetooth",
    "camera",
    "capacitor",
    "charger",
    "chip",
    "circuit",
    "computer",
    "console",
    "cpu",
    "desktop",
    "device",
    "diode",
    "display",
    "drone",
    "earbuds",
    "electrical",
    "electronic",
    "fan",
    "firmware",
    "fridge",
    "gadget",
    "gpu",
    "headphone",
    "hardware",
    "hdmi",
    "ic",
    "inverter",
    "iphone",
    "keyboard",
    "laptop",
    "led",
    "microcontroller",
    "mobile",
    "monitor",
    "motherboard",
    "mouse",
    "pcb",
    "phone",
    "power",
    "printer",
    "processor",
    "ram",
    "raspberry",
    "refrigerator",
    "resistor",
    "router",
    "sensor",
    "smartphone",
    "speaker",
    "tablet",
    "television",
    "transistor",
    "tv",
    "usb",
    "voltage",
    "washing machine",
    "wifi",
    "wire",
}

TOPIC_HINTS = {
    "battery": "Batteries age fastest when they stay hot or sit at 0%/100% for long periods. Use the original charger where possible, avoid heat, and replace swollen batteries immediately.",
    "charger": "Use a charger with matching voltage and enough current rating. A higher amp rating is usually okay because the device draws what it needs, but the wrong voltage can damage hardware.",
    "laptop": "For laptops, start with power, display, storage, RAM, and cooling checks. Keep vents clean, update drivers, and back up data before hardware troubleshooting.",
    "phone": "For phones, check storage, battery health, charging port dust, software updates, and app battery usage. Avoid moisture and low-quality charging accessories.",
    "wifi": "For Wi-Fi issues, restart the router, test close to the router, check 2.4 GHz versus 5 GHz, update firmware, and reduce interference from walls or other electronics.",
    "router": "Routers work best in an open central place. Update firmware, use WPA2/WPA3 security, and change the default admin password.",
    "tv": "For TV problems, check source input, HDMI cable, backlight behavior, sound output, and firmware updates before assuming panel failure.",
    "monitor": "For monitor issues, test another cable and input port, confirm refresh rate settings, and check whether the power LED or backlight turns on.",
    "printer": "For printers, check paper path, ink/toner levels, driver status, Wi-Fi connection, and whether the print queue is stuck.",
    "circuit": "For circuits, verify power rails first, then continuity, polarity, grounding, and component ratings. Always disconnect power before changing wiring.",
    "resistor": "A resistor limits current and drops voltage. Its value is measured in ohms, and its wattage rating must be high enough to avoid overheating.",
    "capacitor": "A capacitor stores charge and is used for filtering, timing, and smoothing power. Mind polarity on electrolytic capacitors.",
    "transistor": "A transistor can work as a switch or amplifier. The common pins are base/gate, collector/drain, and emitter/source depending on the type.",
    "sensor": "Sensors convert physical conditions like light, heat, motion, or distance into electrical signals a circuit or microcontroller can read.",
}


def login_required(route):
    @wraps(route)
    def wrapped(*args, **kwargs):
        if "user_email" not in session:
            return redirect(url_for("login"))
        return route(*args, **kwargs)

    return wrapped


def is_valid_email(email):
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email or "") is not None


def is_electronics_related(message):
    clean = message.lower()
    return any(re.search(rf"\b{re.escape(keyword)}\b", clean) for keyword in ELECTRONICS_KEYWORDS)


def send_login_email(to_email):
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")
    from_email = os.environ.get("SMTP_FROM", username or "electronics-chatbot@example.com")

    if not all([host, username, password]):
        return False, "SMTP is not configured. Login worked, but email was not sent."

    message = EmailMessage()
    message["Subject"] = "ElectroBot login notification"
    message["From"] = from_email
    message["To"] = to_email
    message.set_content(
        "Hello,\n\n"
        "You logged in to ElectroBot, the electronics-only chatbot.\n"
        f"Login time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n\n"
        "If this was not you, please change your password immediately.\n"
    )

    try:
        with smtplib.SMTP(host, port, timeout=12) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(message)
        return True, "Login email sent successfully."
    except Exception as exc:
        return False, f"Login worked, but email sending failed: {exc}"


def electronics_answer(message):
    text = message.lower()
    matched_hints = [
        hint
        for keyword, hint in TOPIC_HINTS.items()
        if re.search(rf"\b{re.escape(keyword)}\b", text)
    ]

    if matched_hints:
        answer = " ".join(matched_hints[:2])
    else:
        answer = (
            "This is an electronics topic. Start by identifying the device model, the symptom, "
            "when it began, and whether power, cables, updates, heat, or physical damage are involved."
        )

    return (
        f"{answer} For safety, unplug mains-powered devices before opening them, and use a qualified "
        "technician for high-voltage parts such as power supplies, TVs, microwave ovens, and inverters."
    )

def groq_electronics_answer(message):
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return electronics_answer(message), "local"

    try:
        client = Groq(api_key=api_key)

        model_name = os.environ.get(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile"
        )

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ElectroBot. "
                        "Answer only electronics and electronic device questions. "
                        "Provide practical and beginner-friendly explanations. "
                        "Include safety warnings when needed."
                    )
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.4,
            max_tokens=500
        )

        reply = response.choices[0].message.content.strip()

        if not reply:
            return electronics_answer(message), "local"

        return reply, "groq"

    except Exception as exc:
        return (
            f"{electronics_answer(message)} (Groq failed: {exc})",
            "local"
        )

@app.route("/")
def home():
    if "user_email" in session:
        return redirect(url_for("chat"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not is_valid_email(email):
        return render_template("login.html", error="Please enter a valid mail ID.", email=email)

    if len(password) < 6:
        return render_template(
            "login.html",
            error="Password must contain at least 6 characters.",
            email=email,
        )

    session["user_email"] = email
    sent, status = send_login_email(email)
    session["mail_status"] = status
    session["mail_sent"] = sent
    return redirect(url_for("chat"))


@app.route("/chat", methods=["GET"])
@login_required
def chat():
    mail_status = session.pop("mail_status", None)
    mail_sent = session.pop("mail_sent", None)
    return render_template(
        "chat.html",
        user_email=session["user_email"],
        mail_status=mail_status,
        mail_sent=mail_sent,
    )


@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"ok": False, "alert": "Please type a question about an electronic device."}), 400

    if not is_electronics_related(message):
        return (
            jsonify(
                {
                    "ok": False,
                    "alert": "Only electronic devices and electronics-related questions are allowed.",
                }
            ),
            422,
        )

    try:
        reply, source = groq_electronics_answer(message)
    except Exception as exc:
        reply = electronics_answer(message)
        source = "local"

    return jsonify({"ok": True, "reply": reply, "source": source})


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()   