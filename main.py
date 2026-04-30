import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, HTMLResponse
import anthropic

app = FastAPI()

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "gw_secret_token")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_KEY")
OWNER_NUMBER = "966569261930"

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

PACKAGES = "1-شهر: 29 ريال | 2-ثلاثة اشهر: 49 ريال | 3-ستة اشهر: 69 ريال | 4-سنة: 99 ريال"
SYSTEM_PROMPT = "انت مساعد مبيعات لمتجر GW للاشتراكات. رد بالعربية باسلوب ودي. باقاتنا: " + PACKAGES + ". اذا اراد الاشتراك اطلب اسمه والباقة ثم اخبره ان الفريق سيتواصل معه."

conversations = {}

@app.get("/webhook")
async def verify(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return PlainTextResponse(params.get("hub.challenge"))
    raise HTTPException(status_code=403)

@app.post("/webhook")
async def receive(request: Request):
    body = await request.json()
    try:
        msg = body["entry"][0]["changes"][0]["value"]["messages"][0]
        from_num = msg["from"]

        if msg.get("type") != "text":
            await send_msg(from_num, "ارسل رسالة نصية وسنساعدك")
            return {"status": "ok"}

        text = msg["text"]["body"]

        print(f"📩 رسالة من {from_num}: {text}")

        # إشعار واتساب لك
        if from_num != OWNER_NUMBER:
            await send_msg(OWNER_NUMBER, f"📩 رسالة جديدة من {from_num}:\n{text}")

        if from_num not in conversations:
            conversations[from_num] = []
        conversations[from_num].append({"role": "user", "content": text})

        if len(conversations[from_num]) > 20:
            conversations[from_num] = conversations[from_num][-20:]

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=conversations[from_num]
        )

        reply = response.content[0].text
        conversations[from_num].append({"role": "assistant", "content": reply})

        print(f"🤖 رد البوت على {from_num}: {reply}")

        await send_msg(from_num, reply)

    except Exception as e:
        print("خطا: " + str(e))

    return {"status": "ok"}

async def send_msg(to, text):
    url = "https://graph.facebook.com/v19.0/" + PHONE_NUMBER_ID + "/messages"
    headers = {"Authorization": "Bearer " + WHATSAPP_TOKEN, "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    async with httpx.AsyncClient() as http:
        await http.post(url, headers=headers, json=payload)

@app.get("/chat", response_class=HTMLResponse)
async def chat_view():
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>محادثات البوت</title>
        <style>
            body { font-family: Arial; background: #111; color: #eee; padding: 20px; }
            h1 { color: #25D366; }
            .contact { background: #1e1e1e; border-radius: 10px; padding: 15px; margin-bottom: 20px; }
            .contact h2 { color: #25D366; margin-bottom: 10px; font-size: 16px; }
            .msg { padding: 8px 12px; border-radius: 8px; margin: 5px 0; max-width: 80%; }
            .user { background: #2a2a2a; margin-left: auto; text-align: right; }
            .bot { background: #1a3a2a; text-align: right; }
            .label { font-size: 11px; color: #888; margin-bottom: 2px; }
            .empty { color: #888; text-align: center; margin-top: 50px; }
        </style>
        <script>
            setTimeout(() => location.reload(), 10000);
        </script>
    </head>
    <body>
        <h1>💬 محادثات البوت</h1>
    """

    if not conversations:
        html += "<p class='empty'>لا توجد محادثات بعد</p>"
    else:
        for number, msgs in conversations.items():
            html += f"<div class='contact'><h2>📱 {number}</h2>"
            for m in msgs:
                role_label = "العميل" if m['role'] == 'user' else "🤖 البوت"
                css_class = "user" if m['role'] == 'user' else "bot"
                html += f"<div class='label'>{role_label}</div>"
                html += f"<div class='msg {css_class}'>{m['content']}</div>"
            html += "</div>"

    html += "</body></html>"
    return HTMLResponse(content=html)

@app.get("/")
async def root():
    return {"status": "GW Bot يعمل"}
