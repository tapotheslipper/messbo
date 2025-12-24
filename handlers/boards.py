import re
from telebot import TeleBot
from controllers import BoardController
from models import Logger
from handlers import DEFAULT_MESSAGE, PREFIX
from datetime import datetime, timezone
import traceback

logger = Logger().get_logger()


def register_board_handlers(bot: TeleBot, controller: BoardController):

    def extract_quoted_name(text):
        pattern = r'/messbo_\w+(?:@\w+)?\s+(?:([\'"`])(.*?)\1|(\S+))'
        find = re.match(pattern, text)
        if find:
            return (find.group(2) or find.group(3)).strip()
        return None

    @bot.message_handler(commands=[PREFIX + "new_board"])
    def new_board_handler(message):
        try:

            if message.chat.type in ["group", "supergroup"]:
                member = bot.get_chat_member(message.chat.id, message.from_user.id)

                if member.status not in ["administrator", "creator"]:
                    bot.reply_to(
                        message,
                        "Данная команда доступна только администраторам группы.",
                    )
                    return

            logger.info(
                f"[NEW BOARD REQUEST] user '{message.from_user.id}': '{message.text}'."
            )

            argument = extract_quoted_name(message.text)
            board, name = controller.create_board(
                message.chat.id, message.from_user.id, argument
            )

            reply = (
                f"Доска {board.name} создана."
                if board
                else f"Не удалось создать доску '{name}'. Возможно, данное имя уже занято."
            )
            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[NEW BOARD ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=[PREFIX + "show_boards"])
    def show_boards_handler(message):
        try:
            boards = controller.show_all_boards(message.chat.id)
            if boards:
                list_text = "\n".join(
                    f"{i + 1}. {board}" for i, board in enumerate(boards)
                )
                reply = f"<b>Список досок в данном чате:</b>\n\n{list_text}"
            else:
                reply = "<i>В этом чате нет досок</i>."

            bot.send_message(message.chat.id, reply, parse_mode="HTML")
        except Exception as exc:
            logger.error(f"[SHOW BOARDS ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=[PREFIX + "show_board"])
    def show_board_handler(message):
        try:
            argument = extract_quoted_name(message.text)
            if not argument:
                bot.send_message(
                    message.chat.id,
                    f"Укажите название доски. Пример: /{PREFIX}show_board 'Моя доска'",
                )
                return

            board = controller.show_one_board(message.chat.id, argument)
            if not board:
                bot.send_message(message.chat.id, f"Доски '{argument}' нет.")
                return

            owner_link = f'<a href="tg://user?id={board.owner_id}">Владелец</a>'
            mod_ids = controller.get_board_moderators(board.id)
            mod_links = (
                ", ".join(
                    [
                        f'<a href="tg://user?id={mod_id}">Модератор</a>'
                        for mod_id in mod_ids
                    ]
                )
                if mod_ids
                else "отсутствуют"
            )

            reply = (
                f"Доска: <b>{board.name}</b>\n"
                f"Владелец: {owner_link}\n"
                f"Модераторы: {mod_links}\n\n"
            )

            entries = controller.get_board_entries(board.id)
            if not entries:
                reply += "<i>На этой доске нет записей</i>"
            else:
                for i, entry in enumerate(entries):
                    dt = datetime.fromisoformat(entry["last_modified_at_utc"]).strftime(
                        "%Y.%m.%d %H:%M:%S"
                    )
                    reply += f"{i + 1}. <b>[{dt}]</b> (ID: {entry["local_id"]}) - {entry["content"]}\n"

            bot.send_message(message.chat.id, reply, parse_mode="HTML")
        except Exception as exc:
            logger.error(f"[SHOW BOARD ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=[PREFIX + "rename"])
    def rename_board_handler(message):
        try:
            pattern = r'/messbo_rename(?:@\w+)?\s+(?:([\'"`])(.*?)\1|(\S+))\s+(?:([\'"`])(.*?)\4|(\S+))'
            find = re.match(pattern, message.text)

            if not find:
                bot.send_message(
                    message.chat.id,
                    f"Некорректный формат команды. Используйте: /{PREFIX}rename 'старое имя' 'новое имя'",
                )
                return

            old_name = (find.group(2) or find.group(3)).strip()
            new_name = (find.group(5) or find.group(6)).strip()

            res = controller.rename_board(
                message.chat.id, message.from_user.id, old_name, new_name
            )
            responses = {
                "renamed": f"Доска '{old_name}' переименована в '{new_name}'.",
                "name_taken": f"Доска с названием '{new_name}' уже существует.",
                "no_access": "У Вас нет прав на редактирование данной доски (вы не модератор/владелец).",
                "not_found": f"Доска '{old_name}' не найдена.",
            }
            bot.send_message(message.chat.id, responses.get(res, DEFAULT_MESSAGE))
        except Exception as exc:
            logger.error(f"[RENAME ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=[PREFIX + "remove_board"])
    def remove_board_handler(message):
        try:
            argument = extract_quoted_name(message.text)

            if not argument:
                bot.send_message(message.chat.id, "Укажите название доски на удаление.")
                return

            ok = controller.remove_board(
                message.chat.id, message.from_user.id, argument
            )

            reply = (
                f"Доска '{argument}' удалена."
                if ok
                else "Доска не найдена или вы не являетесь её владельцем."
            )
            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[REMOVE ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    # entries

    @bot.message_handler(commands=[PREFIX + "add"])
    def add_entry_handler(message):
        try:
            pattern = (
                r'/messbo_add(?:@\w+)?\s+(?:([\'"`])(.*?)\1|(\S+))\s+([\'"`])(.*?)\4'
            )
            find = re.match(pattern, message.text)
            if not find:
                bot.send_message(
                    message.chat.id,
                    f"Неверный формат. Используйте: /{PREIFX}add 'Доска' 'Текст записи'",
                )
                return

            board_name = (find.group(2) or find.group(3)).strip()
            content = find.group(5).strip()

            board = controller.show_one_board(message.chat.id, board_name)

            if not board or not controller._has_access(board.id, message.from_user.id):
                bot.send_message(
                    message.chat.id,
                    "Доска не найдена или у Вас нет прав доступа её редактирования.",
                )
                return

            if controller.add_entry(board.id, message.from_user.id, content):
                bot.send_message(message.chat.id, "Запись добавлена.")
        except Exception as exc:
            logger.error(f"[ADD ENTRY ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=[PREFIX + "edit"])
    def edit_entry_handler(message):
        try:
            pattern = r'/messbo_edit(?:@\w+)?\s+(?:([\'"`])(.*?)\1|(\S+))\s+(\d+)\s+([\'"`])(.*?)\5'
            find = re.match(pattern, message.text)
            if not find:
                bot.send_message(
                    message.chat.id,
                    f"Некорректный формат. Формат: /{PREFIX}edit 'Доска' Локальный ID записи 'Новый текст'",
                )
                return

            board_name = (find.group(2) or find.group(3)).strip()
            local_id = int(find.group(4))
            new_content = find.group(6).strip()

            board = controller.show_one_board(message.chat.id, board_name)
            if not board or not controller._has_access(board.id, message.from_user.id):
                bot.send_message(
                    message.chat.id,
                    "Доска не найдена или у Вас нет прав доступа её редактирования.",
                )
                return

            entry = controller.get_entry_by_local_id(board.id, local_id)
            if not entry:
                bot.send_message(
                    message.chat.id, f"Запись с ID {local_id} не найдена на этой доске."
                )
                return

            if controller.edit_entry(entry.id, new_content):
                bot.send_message(message.chat.id, f"Запись ID {local_id} обновлена.")
        except Exception as exc:
            traceback_text = traceback.format_exc()
            logger.error(f"[EDIT ENTRY ERROR]: '{traceback_text}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=[PREFIX + "remove"])
    def remove_entry_handler(message):
        try:
            pattern = r'/messbo_remove(?:@\w+)?\s+(?:([\'"`])(.*?)\1|(\S+))\s+(\d+)'
            find = re.match(pattern, message.text)
            if not find:
                bot.send_message(
                    message.chat.id,
                    f"Неверный формат команды. Формат: /{PREFIX}remove 'Доска' [ID записи]",
                )
                return

            board_name = (find.group(2) or find.group(3)).strip()
            local_id = int(find.group(4).strip())

            board = controller.show_one_board(message.chat.id, board_name)
            if not board or not controller._has_access(board.id, message.from_user.id):
                bot.send_message(
                    message.chat.id,
                    "Доска не найдена или у Вас не прав доступа на её удаление.",
                )
                return

            entry = controller.get_entry_by_local_id(board.id, local_id)
            if not entry:
                bot.send_message(message.chat.id, f"Запись с ID {local_id} не найдена.")
                return

            if controller.delete_entry(entry.id):
                bot.send_message(message.chat.id, f"Запись с ID {local_id} удалена.")
        except Exception as exc:
            logger.error(f"[REMOVE ENTRY ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)
