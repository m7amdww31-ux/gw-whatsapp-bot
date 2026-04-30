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

TIGER_TV = """
🎯 اشتراكات تايقر تي في - Tiger TV 🎯
🔹 أفضل منصة ترفيهية تجمع كل شيء في مكان واحد!

💰 الأسعار:
📅 شهر واحد: 29 ريال
📅 3 أشهر: 49 ريال
📅 6 أشهر: 70 ريال
📅 سنة كاملة: 99 ريال

🎥 المميزات:
✅ جميع القنوات العربية والعالمية
✅ أحدث الأفلام والمسلسلات
✅ بث مباشر للمباريات بجودة عالية
✅ قسم خاص للأنمي والكورسات
✅ دعم فني متواصل
✅ واجهة سهلة الاستخدام
✅ متوافق مع جميع الأجهزة
✨ ما لقيت فلمك أو مسلسلك؟ اطلبه وسنضيفه لك فوراً!
"""

SPARK_TV = """
⚡ سبارك تي في - Spark TV ⚡
🎬 وجهتك الأولى للترفيه بلا حدود!

💰 الأسعار:
📅 3 أشهر: 70 ريال
📅 6 أشهر: 100 ريال
📅 سنة كاملة: 150 ريال

💎 المميزات:
✅ أقوى البرامج والمنصات
✅ أحدث الأفلام والمسلسلات
✅ بث مباشر لأهم المباريات بجودة عالية
✅ بث مستقر وسرعة عالية
✅ دعم فني على مدار الساعة
🚀 تبي فيلم أو مسلسل معين؟ نضيفه لك فوراً!
"""

TIGER_INSTALL = """
📲 طريقة تحميل برنامج Tiger TV:

📺 لشاشات التلفزيون:
1️⃣ حمل تطبيق Downloader على شاشتك
2️⃣ افتح البرنامج وضع الكود: 5124155
3️⃣ ستظهر لك 6 برامج، اختر أي واحد وثبته
🎬 شرح بالفيديو: https://youtu.be/hC0jWEBBYyw

📱 لأجهزة الأندرويد:
🔗 اختر أي برنامج من: Elvi.xyz

🍎 لأجهزة الآيفون:
البرنامج الأول: https://apps.apple.com/us/app/castora/id6760588570?l=ar
البرنامج الثاني: https://apps.apple.com/us/app/var-player-unlock-your-world/id6477530321?l=ar
البرنامج الثالث: https://apps.apple.com/us/app/next/id6443335504?l=ar
⚠️ كود البرنامج للآيفون: 904
"""

SPARK_INSTALL = """
📲 طريقة تحميل برنامج Spark TV:

📺 لشاشات التلفزيون (برنامج Spark Diamond):
1️⃣ حمل تطبيق Downloader على شاشتك
2️⃣ افتح البرنامج وضع الكود: 759513
3️⃣ سيتم تحميل برنامج SPARK DIAMOND تلقائياً
4️⃣ ضع اشتراكك واستمتع بالمشاهدة
🎬 شرح بالفيديو: https://youtu.be/2qDVm9aprWc

📱 لأجهزة الأندرويد:
🔗 رابط التحميل: 2u.pw/sdi

🍎 لأجهزة الآيفون والآيباد:
البرنامج الأول: https://apps.apple.com/us/app/next/id6443335504?l=ar
البرنامج الثاني: https://apps.apple.com/us/app/castora/id6760588570?l=ar
⚠️ كود البرنامج للآيفون: spark
"""

SYSTEM_PROMPT = f"""انت مساعد مبيعات لمتجر GW يبيع اشتراكات لبرنامجين:
1. تايقر تي في Tiger TV
2. سبارك تي في Spark TV

رد بالعربية باسلوب ودي ومرحب. استخدم كلمة "برنامج" بدل "سيرفر" دائماً.

تفاصيل Tiger TV:
{TIGER_TV}

تفاصيل Spark TV:
{SPARK_TV}

طريقة تحميل برنامج Tiger TV:
{TIGER_INSTALL}

طريقة تحميل برنامج Spark TV:
{SPARK_INSTALL}

تعليمات مهمة:
- رحب بالعميل واعرض عليه البرنامجين
- اخبر العميل ان هناك تجربة مجانية 12 ساعة متاحة للبرنامجين
- إذا سأل عن فيلم أو مسلسل أو قناة معينة، أخبره: "حتى لو ما كان موجود عندنا، ما عليك إلا تطلبه وسنضيفه لك فوراً! 🚀"
- إذا طلب التجربة المجانية اطلب منه:
  1. اسمه
  2. البرنامج الذي يريد تجربته (Tiger TV او Spark TV)
  3. اليوزر نيم (يجب ان يكون 6 خانات بالضبط)
  4. الباسورد (يجب ان يكون 8 خانات بالضبط)
- تحقق ان اليوزر 6 خانات والباسورد 8 خانات، اذا كان خطأ اطلب منه التصحيح
- بعد ما تجمع كل المعلومات اخبره ان الفريق سيفعل التجربة خلال وقت قصير
- إذا سأل عن التحميل اسأله أي برنامج يريد ثم أرسل له دليل التحميل المناسب
- إذا أراد الاشتراك المدفوع اطلب منه اسمه والباقة والبرنامج ثم أخبره أن فريقنا سيتواصل معه قريباً
- لا تستخدم كلمة سيرفر أبداً، استخدم برنامج دائماً
- كن ودياً ومرحباً دائماً"""

conversations = {}
trial_requests = {}
TIGER_IMAGE = "https://ibb.co/Z6qTYzph"
SPARK_IMAGE = "https://ibb.co/CphCvdg6"

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
            await send_msg(from_num, "ارسل رسالة نصية وسنساعدك 😊")
            return {"status": "ok"}

        text = msg["text"]["body"].strip()
        print(f"📩 رسالة من {from_num}: {text}")

        if from_num != OWNER_NUMBER:
            await send_msg(OWNER_NUMBER, f"📩 رسالة جديدة من {from_num}:\n{text}")

        # أول رسالة
        if from_num not in conversations:
            conversations[from_num] = []
            await send_image(from_num, TIGER_IMAGE)
            await send_image(from_num, SPARK_IMAGE)
            await send_msg(from_num,
                "أهلاً بك في متجر GW! 👋\n\n"
                "عندنا برنامجين رائعين:\n\n" +
                TIGER_TV + "\n\n" + SPARK_TV +
                "\n\n🎁 يتوفر تجربة مجانية 12 ساعة للبرنامجين!\n"
                "✨ وحتى لو ما لقيت فلمك أو مسلسلك أو قناتك، اطلبها وسنضيفها لك فوراً!\n\n"
                "كيف أقدر أساعدك؟ 😊"
            )
            return {"status": "ok"}

        # تحقق من طلبات التجربة المجانية
        if from_num in trial_requests:
            trial = trial_requests[from_num]
            step = trial.get("step")

            if step == "program":
                if "tiger" in text.lower() or "تايقر" in text or "1" in text:
                    trial["program"] = "Tiger TV"
                elif "spark" in text.lower() or "سبارك" in text or "2" in text:
                    trial["program"] = "Spark TV"
                else:
                    await send_msg(from_num, "الرجاء اختيار البرنامج:\n1️⃣ Tiger TV\n2️⃣ Spark TV")
                    return {"status": "ok"}
                trial["step"] = "username"
                await send_msg(from_num, f"✅ اخترت {trial['program']}\n\nأرسل لي اليوزر نيم (6 خانات بالضبط) 👇")
                return {"status": "ok"}

            elif step == "username":
                if len(text) != 6:
                    await send_msg(from_num, f"❌ اليوزر نيم يجب أن يكون 6 خانات بالضبط\nأنت أرسلت {len(text)} خانات، حاول مرة ثانية 👇")
                    return {"status": "ok"}
                trial["username"] = text
                trial["step"] = "password"
                await send_msg(from_num, "✅ تم استلام اليوزر نيم\n\nأرسل لي الباسورد (8 خانات بالضبط) 👇")
                return {"status": "ok"}

            elif step == "password":
                if len(text) != 8:
                    await send_msg(from_num, f"❌ الباسورد يجب أن يكون 8 خانات بالضبط\nأنت أرسلت {len(text)} خانات، حاول مرة ثانية 👇")
                    return {"status": "ok"}
                trial["password"] = text
                trial["step"] = "done"

                await send_msg(OWNER_NUMBER,
                    f"🎁 طلب تجربة مجانية جديد!\n"
                    f"📱 الرقم: {from_num}\n"
                    f"👤 الاسم: {trial.get('name', 'غير محدد')}\n"
                    f"📺 البرنامج: {trial['program']}\n"
                    f"🔑 اليوزر: {trial['username']}\n"
                    f"🔒 الباسورد: {trial['password']}"
                )

                await send_msg(from_num,
                    "✅ تم استلام بيانات التجربة المجانية!\n\n"
                    f"📺 البرنامج: {trial['program']}\n"
                    f"🔑 اليوزر: {trial['username']}\n"
                    f"🔒 الباسورد: {trial['password']}\n\n"
                    "⏳ سيتم تفعيل التجربة خلال وقت قصير إن شاء الله 🙏\n"
                    "مدة التجربة: 12 ساعة مجاناً 🎉"
                )
                del trial_requests[from_num]
                return {"status": "ok"}

        # كشف طلب التجربة المجانية
        if any(word in text for word in ["تجربة", "مجانية", "جرب", "trial", "تجريب"]):
            trial_requests[from_num] = {"step": "program", "name": ""}
            await send_msg(from_num, "🎁 رائع! التجربة المجانية 12 ساعة متاحة!\n\nأي برنامج تريد تجربته؟\n1️⃣ Tiger TV\n2️⃣ Spark TV")
            return {"status": "ok"}

        conversations[from_num].append({"role": "user", "content": text})

        if len(conversations[from_num]) > 20:
            conversations[from_num] = conversations[from_num][-20:]

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
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

async def send_image(to, image_url):
    url = "https://graph.facebook.com/v19.0/" + PHONE_NUMBER_ID + "/messages"
    headers = {"Authorization": "Bearer " + WHATSAPP_TOKEN, "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"link": image_url}
    }
    async with httpx.AsyncClient() as http:
        await http.post(url, headers=headers, json=payload)

@app.get("/chat", response_class=HTMLResponse)
async def chat_view():
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>محادثات البوت - GW</title>
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
        <script> setTimeout(() => location.reload(), 10000); </script>
    </head>
    <body>
        <h1>💬 محادثات البوت - GW</h1>
    """

    if not conversations:
        html += "<p class='empty'>لا توجد محادثات بعد</p>"
    else:
        for number, msgs in conversations.items():
            is_trial = number in trial_requests
            html += f"<div class='contact'><h2>📱 {number} {'🎁 طلب تجربة' if is_trial else ''}</h2>"
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
    return {"status": "GW Bot يعمل ✅"}
