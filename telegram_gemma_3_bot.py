from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import os
import logging
from ollama import AsyncClient
import asyncio

TOKEN = os.environ.get('TELEGRAM_GEMMA_3_BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def check_sentence_end(sentence):
    stop = False
    stop_check = ['.', '?', '!', '\n']
    for s in stop_check:
        if s in sentence:
            stop = True
            
    return stop

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ' '.join(context.args)
    gemma_msg = {
      'role': 'user', 
      'content': msg
    }
    
    msg_sent = await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="loading...",
            parse_mode="Markdown"
    )
    
    sentence = []
    async for part in await AsyncClient().chat(model='gemma3', messages=[gemma_msg], stream=True):
        sentence.append(part['message']['content'])
        
        if len(sentence) >= 600:
            break
        
        if len(sentence) % 10 == 0:
            sent = ''.join(sentence).replace('*', '-').replace('--', '*')
        
            try:
                await context.bot.editMessageText(
                    chat_id=update.effective_chat.id,
                    message_id=msg_sent.message_id, 
                    text=sent,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(e)
                
    try:
        await context.bot.editMessageText(
            chat_id=update.effective_chat.id,
            message_id=msg_sent.message_id, 
            text=''.join(sentence).replace('*', '-').replace('--', '*'),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(e)
        
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Greetings, I'm Artoria Pendragon, King of Knights. Pleased to make your acquaintance!"
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('ask', ask))
    
    application.run_polling()