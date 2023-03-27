import telegram

from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder

async def start(update, context):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a bot. How can I help you?")
    except Exception as e:
        print(e)

async def echo(update, context):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="your input=" + update.message.text)
    except Exception as e:
        print(e)

def main():
    try:
        application = ApplicationBuilder().token('{telegram_token}').build()
        start_handler = CommandHandler('start', start)
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
        application.add_handler(start_handler)
        application.add_handler(echo_handler)
        application.run_polling()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
