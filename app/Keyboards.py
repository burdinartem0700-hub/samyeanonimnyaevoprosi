from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUser

username = "@teste32bot"
url_bot_chan = f"https://t.me/{username}?startchannel=start"
url_bot_gr = f"https://t.me/{username}?startgroup=start"
usr_set_conntact = f"https://t.me/{username}?startcontact=start"

back_send = InlineKeyboardMarkup(inline_keyboard =[
    [InlineKeyboardButton(text = "Отменить", callback_data="back_sen")]
])

add_chanal = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "Добавить в канал",url=url_bot_chan)],
        [InlineKeyboardButton(text="Добавить в группу", url=url_bot_gr)]
    ])

set_usr = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Выдать премиум", request_user=KeyboardButtonRequestUser(request_id=1,user_is_bot=False))]
], one_time_keyboard=True, resize_keyboard=True)
