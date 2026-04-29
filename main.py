{\rtf1\ansi\ansicpg1252\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset178 GeezaPro;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh9000\viewkind0
\pard\tqr\tx720\tqr\tx1440\tqr\tx2160\tqr\tx2880\tqr\tx3600\tqr\tx4320\tqr\tx5040\tqr\tx5760\tqr\tx6480\tqr\tx7200\tqr\tx7920\tqr\tx8640\pardirnatural\qr\partightenfactor0

\f0\fs24 \cf0 import os\
import httpx\
from fastapi import FastAPI, Request, HTTPException\
from fastapi.responses import PlainTextResponse\
import anthropic\
\
app = FastAPI()\
\
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "gw_secret_token")\
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")\
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")\
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_KEY")\
\
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)\
\
PACKAGES = """\
\'c8\'c7\'de\'c7\'ca\'e4\'c7 \'dd\'ed GW:\
1\uc0\u65039 \u8419  \'d4\'e5\'d1 \'e6\'c7\'cd\'cf \'97 29 \'d1\'ed\'c7\'e1\
2\uc0\u65039 \u8419  3 \'c3\'d4\'e5\'d1 \'97 49 \'d1\'ed\'c7\'e1\
3\uc0\u65039 \u8419  6 \'c3\'d4\'e5\'d1 \'97 69 \'d1\'ed\'c7\'e1\
4\uc0\u65039 \u8419  \'d3\'e4\'c9 \'df\'c7\'e3\'e1\'c9 \'97 99 \'d1\'ed\'c7\'e1\
\'cc\'e3\'ed\'da \'c7\'e1\'c8\'c7\'de\'c7\'ca \'ca\'d4\'e3\'e1: \'c3\'dd\'e1\'c7\'e3\'a1 \'e3\'d3\'e1\'d3\'e1\'c7\'ca\'a1 \'e6\'c8\'cb \'e3\'c8\'c7\'d1\'ed\'c7\'ca \'e3\'c8\'c7\'d4\'d1 \'da\'e1\'ec \'cc\'e3\'ed\'da \'c3\'cc\'e5\'d2\'ca\'df.\
"""\
\
SYSTEM_PROMPT = f"""\'c3\'e4\'ca \'e3\'d3\'c7\'da\'cf \'e3\'c8\'ed\'da\'c7\'ca \'e1\'e3\'ca\'cc\'d1 GW \'e1\'e1\'c7\'d4\'ca\'d1\'c7\'df\'c7\'ca. \'d1\'cf\'f8 \'c8\'c7\'e1\'da\'d1\'c8\'ed\'c9 \'c8\'c3\'d3\'e1\'e6\'c8 \'e6\'cf\'ed \'e6\'e3\'ce\'ca\'d5\'d1.\
\'c8\'c7\'de\'c7\'ca\'e4\'c7: \{PACKAGES\}\
\'c5\'d0\'c7 \'c3\'d1\'c7\'cf \'c7\'e1\'c7\'d4\'ca\'d1\'c7\'df \'c7\'d8\'e1\'c8 \'c7\'d3\'e3\'e5 \'e6\'c7\'e1\'c8\'c7\'de\'c9 \'c7\'e1\'ca\'ed \'ed\'d1\'ed\'cf\'e5\'c7\'a1 \'cb\'e3 \'c3\'ce\'c8\'d1\'e5 \'c3\'e4 \'c7\'e1\'dd\'d1\'ed\'de \'d3\'ed\'ca\'e6\'c7\'d5\'e1 \'e3\'da\'e5 \'de\'d1\'ed\'c8\'c7\'f0."""\
\
conversations = \{\}\
\
@app.get("/webhook")\
async def verify(request: Request):\
    params = dict(request.query_params)\
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:\
        return PlainTextResponse(params.get("hub.challenge"))\
    raise HTTPException(status_code=403)\
\
@app.post("/webhook")\
async def receive(request: Request):\
    body = await request.json()\
    try:\
        msg = body["entry"][0]["changes"][0]["value"]["messages"][0]\
        from_num = msg["from"]\
        if msg.get("type") != "text":\
            await send_msg(from_num, "\'c3\'d1\'d3\'e1 \'d1\'d3\'c7\'e1\'c9 \'e4\'d5\'ed\'c9 \'e6\'d3\'e4\'d3\'c7\'da\'cf\'df \uc0\u55357 \u56842 ")\
            return \{"status": "ok"\}\
        text = msg["text"]["body"]\
        if from_num not in conversations:\
            conversations[from_num] = []\
        conversations[from_num].append(\{"role": "user", "content": text\})\
        if len(conversations[from_num]) > 20:\
            conversations[from_num] = conversations[from_num][-20:]\
        response = client.messages.create(\
            model="claude-sonnet-4-20250514",\
            max_tokens=500,\
            system=SYSTEM_PROMPT,\
            messages=conversations[from_num]\
        )\
        reply = response.content[0].text\
        conversations[from_num].append(\{"role": "assistant", "content": reply\})\
        await send_msg(from_num, reply)\
    except Exception as e:\
        print(f"\'ce\'d8\'c3: \{e\}")\
    return \{"status": "ok"\}\
\
async def send_msg(to, text):\
    url = f"https://graph.facebook.com/v19.0/\{PHONE_NUMBER_ID\}/messages"\
    headers = \{"Authorization": f"Bearer \{WHATSAPP_TOKEN\}", "Content-Type": "application/json"\}\
    payload = \{"messaging_product": "whatsapp", "to": to, "type": "text", "text": \{"body": text\}\}\
    async with httpx.AsyncClient() as http:\
        await http.post(url, headers=headers, json=payload)\
\
@app.get("/")\
async def root():\
    return \{"status": "GW Bot \'ed\'da\'e3\'e1"\}}