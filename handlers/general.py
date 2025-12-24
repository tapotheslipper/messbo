from telebot import TeleBot, types
from handlers import HELP_TEXT, PREFIX


def register_general_handlers(bot: TeleBot):
    @bot.message_handler(commands=["start"], chat_types=["private"])
    def start_alias_handler(message):
        start_handler(message)

    @bot.message_handler(commands=[PREFIX + "start"])
    def start_handler(message):

        markup = types.InlineKeyboardMarkup()
        help_button = types.InlineKeyboardButton(
            text="Показать список команд", callback_data="show_help"
        )

        markup.add(help_button)

        bot.send_message(
            message.chat.id,
            "Здравствуйте. Вас приветствует бот <b>MessBo - Доска Объявлений</b>.\n"
            f"Для списка команд воспользуйтесь /{PREFIX}help\n",
            parse_mode="HTML",
            reply_markup=markup,
        )

    @bot.message_handler(commands=[PREFIX + "help"])
    def help_handler(message):
        bot.send_message(message.chat.id, HELP_TEXT, parse_mode="HTML")

    @bot.callback_query_handler(func=lambda call: call.data == "show_help")
    def callback_help(call):
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, HELP_TEXT, parse_mode="HTML")
