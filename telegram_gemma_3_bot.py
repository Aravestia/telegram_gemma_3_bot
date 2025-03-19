from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import os
import logging
from ollama import AsyncClient
import asyncio
import json

TOKEN = os.environ.get('TELEGRAM_GEMMA_3_BOT_TOKEN')
MODEL = 'gemma3'
MAX_MSG_LEN = 600
MAX_CHUNK_LEN = 10
HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")

with open(HISTORY_PATH, 'r') as file:
    history = json.load(file)

print(history)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Greetings, I'm Artoria Pendragon, King of Knights. Pleased to make your acquaintance!"
    )

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.effective_chat.id
    
    async def send_msg(msg, msg_list):
        try:
            await context.bot.editMessageText(
                chat_id=id,
                message_id=msg.message_id, 
                text=''.join(msg_list).replace('*', '-').replace('--', '*'),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(e)
    
    msg = await context.bot.send_message(
            chat_id=id, 
            text="loading...",
            parse_mode="Markdown"
    )
    msg_list = []
    prompt = {
        'role': 'user', 
        'content': ' '.join(context.args)
    }
    
    if str(id) not in history:
        history[str(id)] = [prompt]
    else:
        history[str(id)].append(prompt)
    
    async for chunk in await AsyncClient().chat(model=MODEL, messages=history[str(id)], stream=True):
        msg_list.append(chunk['message']['content'])
        
        if len(msg_list) > MAX_MSG_LEN:
            break
        
        if len(msg_list) % MAX_CHUNK_LEN == 0:   
            await send_msg(msg, msg_list)
            
    await send_msg(msg, msg_list)          
    output = {
        'role': 'assistant',
        'content': ''.join(msg_list).replace('*', '-').replace('--', '*')
    }
    
    history[str(id)].append(output)
    with open(HISTORY_PATH, 'w') as file:
        json.dump(history, file)
        
    print(history)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('ask', ask))
    
    application.run_polling()