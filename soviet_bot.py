import logging
import random
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

logging.basicConfig(level=logging.INFO)

AGENTS = {
    "elena": {"name": "Елена — Стратег 📊", "system": "Ты Елена — эксперт по YouTube Shorts в нише Soviet Stories. Только Shorts до 60 сек. Темы: Чаушеску, Секуритате, советские катастрофы. Постить 2-3 в день. Отвечай 3-4 предложения без приветствий на русском."},
    "alex": {"name": "Александр — Контент 🎬", "system": "Ты Александр — эксперт по Shorts для ниши Soviet Stories. Архивы на archive.org, уникализация через ElevenLabs + субтитры + музыка, монтаж в CapCut. Отвечай 3-4 предложения без приветствий на русском."},
    "sergey": {"name": "Сергей — Мотивация 🔥", "system": "Ты Сергей — мотиватор для авторов Shorts Soviet Stories. Shorts набирают 100к-1млн, не нужна камера, 30 Shorts = результат. Отвечай 2-3 предложения без приветствий на русском."}
}

def pick_agent(text):
    lower = text.lower()
    if any(w in lower for w in ["монтаж","архив","capcut","хук","озвучк","уникал"]):
        return "alex"
    elif any(w in lower for w in ["боюсь","мотив","устал","страшно"]):
        return "sergey"
    return random.choice(["elena","alex","sergey"])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    agent_key = pick_agent(user_text)
    agent = AGENTS[agent_key]
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    history = context.user_data.get("h", [])
    history.append({"role": "user", "content": user_text})
    msg = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=300, system=agent["system"], messages=history[-6:])
    reply = msg.content[0].text
    history.append({"role": "assistant", "content": reply})
    context.user_data["h"] = history
    await update.message.reply_text(f"*{agent['name']}*\n\n{reply}", parse_mode="Markdown")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
