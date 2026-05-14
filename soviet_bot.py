import logging
import random
import asyncio
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

logging.basicConfig(level=logging.INFO)

AGENTS = {
    "elena": {
        "name": "Елена — Стратег 📊",
        "system": "Ты Елена — эксперт по YouTube Shorts в нише Soviet Stories. Только Shorts до 60 сек. Знаешь темы которые взрывают (Чаушеску, Секуритате, советские катастрофы), алгоритм Shorts, монетизация 1000 подп + 10 млн просмотров за 90 дней, постить 2-3 в день в 18-21ч. Отвечай 3-4 предложения, без приветствий, на русском."
    },
    "alex": {
        "name": "Александр — Контент 🎬",
        "system": "Ты Александр — эксперт по созданию Shorts для ниши Soviet Stories. Знаешь где брать архивы (archive.org, Romania communism footage на YouTube), уникализация через озвучку ElevenLabs + субтитры + музыка, монтаж в CapCut, хуки первые 3 сек. Отвечай 3-4 предложения, без приветствий, на русском."
    },
    "sergey": {
        "name": "Сергей — Мотивация 🔥",
        "system": "Ты Сергей — мотиватор для авторов Shorts в нише Soviet Stories. Shorts набирают 100к-1млн легко, не нужна камера, 30 Shorts = первые результаты. Отвечай 2-3 предложения, без приветствий, заряжай энергией, на русском."
    }
}

def pick_agent(text):
    lower = text.lower()
    if any(w in lower for w in ["заголов","монтаж","уникал","архив","capcut","хук","озвучк","страйк"]):
        return "alex"
    elif any(w in lower for w in ["боюсь","мотив","устал","сдаться","страшно"]):
        return "sergey"
    elif any(w in lower for w in ["алгоритм","тема","монетиз","подписчик","план"]):
        return "elena"
    return random.choice(["elena","alex","sergey"])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    agent_key = pick_agent(user_text)
    agent = AGENTS[agent_key]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    history = context.user_data.get("history", [])
    history.append({"role": "user", "content": user_text})
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=agent["system"],
        messages=history[-10:]
    )
    reply = msg.content[0].text
    history.append({"role": "assistant", "content": reply})
    context.user_data["history"] = history
    await update.message.reply_text(f"*{agent['name']}*\n\n{reply}", parse_mode="Markdown")

async def post_init(application):
    pass

def main():
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
