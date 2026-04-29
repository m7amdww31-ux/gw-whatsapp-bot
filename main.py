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

PACKAGES = """
باقاتنا في GW:
1 - شهر واحد: 29 ريال
2 - 3 اشهر: 49 ريال
3 - 6 اشهر: 69 ريال
4 - سنة كاملة: 99 ريال
جميع الباقات تشمل افلام ومسلسلات وبث مباريات مباشر
"""

SYSTEM_PROMPT = f"""انت مساعد مبيعات لمتجر GW للاشتراكات. رد بالعربية باسلوب ودي.
باقاتنا: {PACKAGES}
اذا اراد الاشتراك اطلب اسمه والباقة التي يريدها ثم اخبره ان الفريق سيتواصل معه."""

conversations = {}

@app.get("/webhook")
async
