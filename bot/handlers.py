from telebot import TeleBot
from bot import BoardManager
from models import Logger

logger = Logger().get_logger()

def register_handlers(bot: TeleBot, manager: BoardManager):
    @bot.message_handler(content_types=['text'])
    def text_handler(message):
        try:
            userid = message.from_user.id
            username = message.from_user.username
            logger.info(f"Message received from '{username}': '{message.text}'")
            text = message.text.strip()

            parts = text.split(maxsplit=1)
            cmd = parts[0].lower()
            argument = parts[1] if (len(parts) > 1) else (None)
            
            match (cmd):
                case "/messbo_help":
                    bot.send_message(userid, """
/messbo_new_board <название> = Создать новую доску, название необязательно
/messbo_show_boards = Показать все Ваши доски
/messbo_show_board <название> = Показать Вашу доску с данным названием
""")

                case "/messbo_new_board":
                    board = manager.create_board(userid, argument)
                    if board:
                        message = f"Доска {board.name} создана."
                    else:
                        message = "Не удалось создать доску. Попробуйте позже."
                    bot.send_message(userid, message)
                
                case "/messbo_show_boards":
                    boards_list = manager.show_all_boards(userid)
                    if boards_list:
                        message = "\n".join(f"{i + 1}. {boards_list[i]}" for i in range(len(boards_list)))
                    else:
                        message = "У вас нет досок."
                    bot.send_message(userid, message)
                
                case "/messbo_show_board":
                    board_name = None
                    if (argument):
                        board_name = manager.show_one_board(userid, argument)
                    if (board_name):
                        message = board_name
                    else:
                        message = f"Доски с названием {argument} нет." if argument else "Пожалуйста, укажите название доски."
                    bot.send_message(userid, message)
                
                case _:
                    bot.send_message(userid, "Напишите '/messbo_help' для списка команд.")
        except Exception as exc:
            logger.error(f"Error in handler: '{exc}';")
            bot.send_message(userid, "Произошла ошибка. Попробуйте позже.")
