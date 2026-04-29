import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import anthropic

app = FastAPI()

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "gw_secret_token")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_KEY")

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
        if from_num not in conversations:
            conversations[from_num] = []
        conversations[from_num].append({"role": "user", "content": text})
        if len(conversations[from_num]) > 20:
            conversations[from_num] = conversations[from_num][-20:]
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=conversations[from_num]
        )
        reply = response.content[0].text
        conversations[from_num].append({"role": "assistant", "content": reply})
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

@app.get("/")
async def root():
    return {"status": "GW Bot يعمل"}
