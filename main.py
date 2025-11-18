import telebot
bot = telebot.TeleBot('8159325387:AAFFB1bsQcNggwsPOqU-IimxbfI_lP4Eo6I')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    match (message.text):
        case 'Привет':
            bot.send_message(message.from_user.id, "Привет")
        case '/help':
            bot.send_message(message.from_user.id, 'Напиши "Привет"')
        case _:
            bot.send_message(message.from_user.id, 'Для списка комманд напиши "/help"')

bot.polling(none_stop=True, interval=0)
