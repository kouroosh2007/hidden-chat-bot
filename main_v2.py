import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
import uvicorn

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
URL = os.getenv("RENDER_EXTERNAL_URL")

app = Application.builder().token(TOKEN).build()

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    txt = update.message.text or "<بدون محتوا>"
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 پیام جدید:\n👤 @{user.username or 'بدون یوزرنیم'}\n🆔 {user.id}\n💬 {txt}"
    )

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

async def telegram_endpoint(request: Request) -> Response:
    data = await request.json()
    update = Update.de_json(data, bot=app.bot)
    await app.update_queue.put(update)
    return Response()

async def health(request: Request) -> PlainTextResponse:
    return PlainTextResponse(content="OK")

starlette_app = Starlette(routes=[
    Route("/telegram", telegram_endpoint, methods=["POST"]),
    Route("/healthcheck", health, methods=["GET"]),
])

def main():
    app.bot.set_webhook(url=f"{URL}/telegram")
    uvicorn.run(starlette_app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

if __name__ == "__main__":
    main()
