import logging
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

audio_dir = 'C:/Users/Ericka/Desktop/Oss_tg_bot/audio'
answers_dir = 'C:/Users/Ericka/Desktop/Oss_tg_bot/answers'
os.makedirs(answers_dir, exist_ok=True)

try:
    audio_data = pd.read_excel('C:/Users/Ericka/Desktop/Oss_tg_bot/audio.xlsx', header=None)[0].tolist()
except Exception as e:
    logger.error(f"Ошибка при загрузке файла с аудио: {e}")
    audio_data = []

def create_keyboard():
    keyboard = [
        [InlineKeyboardButton("Поддержать осетинский язык", callback_data='support')],
        [InlineKeyboardButton("Меню", callback_data='menu')],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context):
    reply_markup = create_keyboard()
    welcome_message = (
        "   👋 Приветствуем вас в нашем боте для поддержки осетинского языка! 🌟 \n"
        "   Здесь вы можете написать мини-диктант и помочь нам выявить распространенные ошибки, что очень важно для развития осетинского языка. ✍️ \n"
        "   Ваши диктанты помогут нам лучше понять, какие аспекты языка требуют внимания и совершенствования. 🎓 \n"
        "   Также в нашем боте вы найдете материалы для изучения осетинского языка из самоучителя Ф.М. Таказова 'Самоучитель осетинского языка'. 🔥 \n"
        "   Спасибо за ваш вклад в развитие и поддержку осетинского языка! 🤖 Начните свое путешествие по осетинскому языку уже сегодня! \n"
        "   💬 Если у вас есть вопросы или предложения, пишите нам в личные сообщения. 👋 \n"
        "   Бот разработан для всех, кто хочет изучать и поддерживать осетинский язык. Присоединяйтесь и становитесь частью нашей языковой сообщества! 🌐"
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'support':
        await support_ossetian_language(update, context)
    elif query.data == 'menu':
        await menu_command(update, context)

async def support_ossetian_language(update: Update, context):
    message_text = "Это мини-диктант для поддержки осетинского языка. 📝 Напишите то, что услышали в аудиозаписи"
    reply_markup = create_keyboard()
    await update.callback_query.edit_message_text(text=message_text, reply_markup=reply_markup)

    await send_dictation(update, context)

async def send_dictation(update: Update, context):
    audio_files = os.listdir(audio_dir)
    if audio_files:
        audio_file = random.choice(audio_files)
        audio_number = audio_file.split('-')[0].strip()  # Получаем номер аудиозаписи
        audio_path = os.path.join(audio_dir, audio_file)
        await update.callback_query.message.reply_audio(audio=open(audio_path, 'rb'))
        context.user_data['current_audio_number'] = audio_number  # Сохраняем номер аудиозаписи в контексте
    else:
        await update.callback_query.message.reply_text("Извините, нет доступных аудиозаписей.")

async def handle_message(update: Update, context):
    user_text = update.message.text
    user_id = update.message.from_user.id

    try:
        audio_number = context.user_data.get('current_audio_number', 'unknown')
        answers_files = os.listdir(answers_dir)
        next_file_number = len(answers_files) + 1
        text_file_path = os.path.join(answers_dir, f'answer_{next_file_number}_{audio_number}.txt')

        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write(user_text)

        await update.message.reply_text("Спасибо за ваш ответ! Он сохранен.")
    except Exception as e:
        logger.error(f"Ошибка при записи ответа пользователя: {e}")
        await update.message.reply_text("Произошла ошибка при сохранении ответа. Попробуйте еще раз.")

async def help_command(update: Update, context):
    await update.message.reply_text("👋 Приветствуем вас в нашем боте для поддержки осетинского языка! 🌟 \n"
        "   Здесь вы можете написать мини-диктант и помочь нам выявить распространенные ошибки, что очень важно для развития осетинского языка. ✍️ \n"
        "   Ваши диктанты помогут нам лучше понять, какие аспекты языка требуют внимания и совершенствования. 🎓 "
        "   Также в нашем боте вы найдете материалы для изучения осетинского языка из самоучителя Ф.М. Таказова 'Самоучитель осетинского языка'. 🔥 \n"
        "   Спасибо за ваш вклад в развитие и поддержку осетинского языка! 🤖 Начните свое путешествие по осетинскому языку уже сегодня! \n"
        "   💬 Если у вас есть вопросы или предложения, пишите нам в личные сообщения. 👋 \n"
        "   Бот разработан для всех, кто хочет изучать и поддерживать осетинский язык. Присоединяйтесь и становитесь частью нашей языковой сообщества! 🌐"
    )

async def menu_command(update: Update, context):
    commands_list = [
        "/start - Начать диалог с ботом",
        "/help - Краткая информация о проекте"
    ]
    message_text = "Доступные команды:\n" + "\n".join(commands_list)
    await update.callback_query.edit_message_text(text=message_text, reply_markup=create_keyboard())

def main():
    application = ApplicationBuilder().token("7207211232:AAGOGKdjH96gfdwGr64n5k2uP-R4JmdkMTc").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
