from telebot import TeleBot, types
from handlers import (
    register_general_handlers,
    register_board_handlers,
    register_request_handlers,
    register_fallback,
    COMMANDS,
)


def register_handlers(bot: TeleBot, controllers: dict[str, object]) -> None:

    bot.set_my_commands(COMMANDS, scope=types.BotCommandScopeDefault())

    register_general_handlers(bot)
    register_board_handlers(bot, controllers["board"])
    register_request_handlers(bot, controllers["request"], controllers["board"])
    register_fallback(bot)
