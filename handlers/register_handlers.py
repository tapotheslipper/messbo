from telebot import TeleBot
from handlers import (
    register_general_handlers,
    register_board_handlers,
    register_request_handlers,
    register_fallback,
)
from controllers import BoardController, RequestController


def register_handlers(bot: TeleBot, controllers: dict[str, object]) -> None:
    register_general_handlers(bot)
    register_board_handlers(bot, controllers["board"])
    register_request_handlers(bot, controllers["request"], controllers["board"])
    register_fallback(bot)
