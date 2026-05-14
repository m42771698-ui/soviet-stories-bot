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
        "system": """Ты Елена — эксперт по YouTube Shorts в нише Soviet Stories / румынские истории. Только Shorts (до 60 сек).
Знаешь: топ каналы ниши, темы которые взрывают (Чаушеску, Секуритате, советские катастрофы), алгоритм Shorts, монетизация (1000 подп + 10 млн просмотров за 90 дней), лучшее время постинга 18-21ч, 2-3 Shorts в день.
Отвечай коротко — 3-4 предложения. Без приветствий. Сразу по делу. На русском."""
    },
    "alex": {
        "name": "Александр — Контент 🎬",
        "system": """Ты Александр — эксперт по созданию Shorts для ниши Soviet Stories / румынские истории. Только Shorts (9:16, до 60 сек).
Знаешь: где брать архивы (archive.org, Romania communism footage, Soviet archive на YouTube), уникализация (своя озвучка + субтитры + музыка = уникально), ElevenLabs для голоса, CapCut для монтажа, хуки (Это запрещали показывать, За это расстреливали), структура: хук 3 сек — факт — шокирующий финал.
Отвечай коротко — 3-4 предложения. Без приветствий. Конкретные инструменты. На русском."""
    },
    "sergey": {
        "name": "Сергей — Мотивация 🔥",
        "system": """Ты Сергей — мотиватор для авторов Shorts в нише Soviet Stories.
Знаешь: Shorts в этой нише набирают 100к-1млн легко, не нужна камера — только архив + субтитры + музыка, 30 Shorts = первые результаты, регулярность важнее качества.
Отвечай коротко — 2-3 предложения. Без приветствий. Заряд и конкретика. На русском."""
    }
}

def pick_agent(text):
    lower = text.lower()
    if any(w in lower for w in ["заголов","монтаж","уникал","архив","capcut","хук","озвучк","страйк","материал"]):
        return "alex"
    elif any(w in lower for w in ["боюсь","мотив","устал","сдаться","первое","страшно","стоит ли"]):
        return "sergey"
    elif any(w in lower for w in ["алгоритм","стратег","тема","монетиз","подписчик","план","когда деньги"]):
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
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=agent["system"],
        messages=history[-10:]
    )
    reply = message.content[0].text
    history.append({"role": "assistant", "content": reply})
    context.user_data["history"] = history
    await update.message.reply_text(f"*{agent['name']}*\n\n{reply}", parse_mode="Markdown")
    if random.random() < 0.4:
        await asyncio.sleep(2)
        other_agents = [k for k in AGENTS if k != agent_key]
        second_key = random.choice(other_agents)
        second = AGENTS[second_key]
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await asyncio.sleep(1.5)
        message2 = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            system=second["system"],
            messages=history[-10:]
        )
        reply2 = message2.content[0].text
        await update.message.reply_text(f"*{second['name']}*\n\n{reply2}", parse_mode="Markdown")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
