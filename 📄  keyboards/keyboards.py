from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Мой альбом")
    builder.button(text="📊 Прогресс")
    builder.button(text="🔄 Обмен")
    builder.button(text="➕ Добавить карточки")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

def album_sections_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Введение (1-25)", callback_data="section_intro")
    builder.button(text="🏒 Команды (26-399)", callback_data="section_teams")
    builder.button(text="⭐ Топ-игроки (400-413)", callback_data="section_top")
    builder.button(text="🌟 Восходящие звёзды (414-427)", callback_data="section_rising")
    builder.button(text="🏆 Winner 2024 (428-430)", callback_data="section_winner")
    builder.button(text="🥇 My Golden Team", callback_data="section_golden")
    builder.button(text="🔙 Назад", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()

