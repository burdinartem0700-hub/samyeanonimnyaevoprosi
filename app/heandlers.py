import asyncio
import json
import os
import types
import urllib.parse

from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton,  SwitchInlineQueryChosenChat
import app.Keyboards as kb
import app.DARABASE as a
from aiogram.fsm.context import FSMContext
from app.states import idea

router = Router()
user_referrer = {}
ADMINS = [7555843363]
idPremUsr = []
awaiting_replay = {}
info_message = {}
replay_id = {}
delete_mes_usr = {}
repli_await = {}

@router.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject):
    args = command.args
    a.ensure_user_exists(message.from_user.id)
    user = message.from_user
    user_id = user.id
    if args:
        try:
            referrer_id = int(args)
            await message.delete()
            a.add_ref(user_id)
        except ValueError:
            await message.answer("❌Неверная реферальная ссылка.")
            return
        user_referrer[user_id] = referrer_id
        mesid = await message.answer(
            "📣Напишите любое сообщение.\nВы можете отправить 🖋️текст, 📹видео, 🌠фото, 🔊аудио и тд.", reply_markup=kb.back_send)
        info_message[user_id] = mesid.message_id
    else:
        bot_me = await message.bot.get_me()
        ref_link = f"https://t.me/{bot_me.username}?start={user_id}"
        send_url = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить ссылку",
                                  url=f"https://t.me/share/url?text=💌 Здесь ты можешь отправить мне анонимные сообщения!\n\n📎{ref_link}")]
        ])
        await message.answer(
            f"💌Здесь вы можете получать анонимные сообщения!!\n\n"
            f"📎Ваша ссылка:\n{ref_link}\n\n"
            f"👥С помощью этой ссылке, люди смогут писать вам анонимные сообщения!!", reply_markup=send_url
        )
        if a.is_admin(user_id):
            await message.answer(text = "Вы можете добавить в админы: ", reply_markup=kb.set_usr)
@router.message(Command("static"))
async def static_info(message:Message):
    statis= a.get_ctatic(message.from_user.id)
    send_mes, gec_mes, ref = statis
    await message.answer(f"📈Здесь вы можете посмотреть свою статистику:\n\n<blockquote>👤Перешло по ссылке: {ref}\n📥Отправлено вами сообщений: {gec_mes}\n💌Получено сообщений: {send_mes}</blockquote>\n\n📥Для увелечения статистики присылайте друзьям, знакомомым совим друзьям!", parse_mode="HTML")

@router.message(F.user_shared)
async def set_info(message: Message, bot: Bot):
    shared = message.user_shared.user_id
    if a.is_admin(shared):
         await message.answer("❌Этот пользователь уже премиум!")
         return
    try:
        chat = await bot.get_chat(shared)
        first_name = chat.first_name
        username = chat.username or "None"
    except Exception:
        first_name = " "
        username = None
        await message.answer("❌Пользователя невозможно добавить, так как он еще ни разу не писал боту")
    if message.from_user.id in ADMINS:
        a.add_premium(shared,
                    first_name,
                    username)
        await message.answer(f"Премиум {first_name} был успешно выдан!")
        await message.bot.send_message(chat_id=shared, text = "Поздравляем, вы стали обладателем премиума!")

@router.message(Command("idea"))
async def idea_usr(message: Message, state: FSMContext):
    await state.set_state(idea.idea_text)
    await message.answer("Напишите о том, как бы вы улучшили бота:", reply_markup=kb.back_send)

@router.message(idea.idea_text)
async def add_text_idea(message: Message, state: FSMContext):
    if message.text:
        await message.bot.send_message(chat_id=ADMINS[0], text = f"Пользователь {message.from_user.id} {message.from_user.username} Предлагает"
                                                                 f"\n\n<blockquote>{message.text}</blockquote>\n", parse_mode="HTML")


@router.message(Command("premiumus"))
async def all_admins(message: Message):
    text = f"Все премиум-пользователи бота: \n\n"
    if a.is_admin(message.from_user.id):
        premiums = a.get_premium()
        for premium in premiums:
            ida, first, username = premium
            text += f"Id: <code>{ida}</code>\n"
            text += f"Имя: {first}\n"
            text += f"Юзернейм: @{username}\n\n"
        await message.answer(text + f"\nДля того чтобы дать премиум, воспользуйтесь кнопкой Добавить премиум"
                                    f"\nДля снятия прав админа, используйте команду /delprem (id пользователя, которого хотите удалить)",
                             parse_mode="HTML")

@router.message(Command("delprem"))
async def del_admins(message: Message, command: CommandObject):
    args = command.args
    if args:
        try:
            id_us = int(args)
            if id_us == message.from_user.id:
                return
            a.del_prem(id_us)
            await message.bot.send_message(chat_id=id_us, text = "Вы больше не премиум пользователь")
            await message.answer("Вы успешно сняли премиум с пользователя")
        except ValueError:
            await message.answer("❌ОШИБКА. ID передан неверено")
    else:
        await message.answer("❌Вы не передали id пользователя")

@router.message()
async def forward_to_referrer(message: Message):
    user_id = message.from_user.id
    mesid = 0

    if user_id in user_referrer:
        referrer_id = user_referrer.pop(user_id)
        replay_id[user_id] = referrer_id
        bot_me = await message.bot.get_me()
        ref_link = f"https://t.me/{bot_me.username}?start={user_id}"
        send_url = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить ссылку",
                                  url=f"tg://msg_url?text=" + urllib.parse.quote(
                                      "💌 Здесь ты можешь отправить мне анонимные сообщения!\n\n📎{ref_link}"))]
        ])
        delte_key = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Удалить сообщенние", callback_data=f"delet_{referrer_id}")],
            [InlineKeyboardButton(text="Написать еще", callback_data=f"writing_{referrer_id}")]
        ])
        try:
            if message.text:
                text = f"💬 Вам пришло сообщение:\n\n<blockquote>{message.text}</blockquote>\n\nСвайпните для ответа👈"
                mesid= await message.bot.send_message(chat_id=referrer_id, text=text, parse_mode="HTML")
                if a.is_prem(referrer_id):
                    await message.bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nимя = {message.from_user.first_name}\nайди = {message.from_user.id}")
            elif message.photo:
                file_id = message.photo[-1].file_id
                cap = message.caption + "\n\nСвайпните для ответа👈"
                mesid = await message.bot.send_photo(chat_id=referrer_id, photo=file_id, caption=cap)
                if a.is_prem(referrer_id):
                    await message.bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.video:
                file_id = message.video.file_id
                cap = message.caption + "\n\nСвайпните для ответа👈"
                mesid = await message.bot.send_video(chat_id=referrer_id, video=file_id, caption= cap)
                if a.is_prem(referrer_id):
                    await message.bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.audio:
                file_id =message.audio.file_id
                cap = message.caption + "\n\nСвайпните для ответа👈"
                mesid = await message.bot.send_audio(chat_id=referrer_id, audio=file_id, caption=cap)
                if a.is_prem(referrer_id):
                    await message.bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.voice:
                file_id = message.voice.file_id
                cap = message.caption + "\n\nСвайпните для ответа👈"
                mesid = await message.bot.send_voice(chat_id=referrer_id, voice=file_id, caption=cap)
                if a.is_prem(referrer_id):
                    await message.bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            await message.reply("✅ Сообщение отправлено.", reply_markup=delte_key)
            await message.answer(
                f"💌Здесь вы можете получать анонимные сообщения!!\n\n"
                f"📎 Ваша  ссылка:\n{ref_link}\n\n"
                f"👥C помощью этой ссылке, люди смогут писать вам анонимные сообщения!!", reply_markup=send_url
            )
            a.add_rec_mes(referrer_id)
            a.add_send_mes(user_id)
        except Exception as e:
            await message.reply("❌Не удалось доставить сообщение.")
        delete_mes_usr[user_id] = mesid.message_id
        repli_await[mesid.message_id] = user_id

    if user_id in info_message:
        try:
            await message.bot.delete_message(chat_id=user_id, message_id=info_message[user_id])
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
                mesid = await message.bot.send_message(chat_id=id_usr,
                                               text=f"📩 Вам ответили на ваше сообщение:\n\n<blockquote>{message.text}</blockquote>\n\nСвайпните для ответа⏩"
                                               )
                if a.is_prem(id_usr):
                    await message.bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.photo:
                file_id = message.photo[-1].file_id
                cap = message.caption + "\n\nСвайпните для ответа👈"
                mesid = await message.bot.send_photo(chat_id=id_usr, photo=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}"
                                             )
                if a.is_prem(id_usr):
                    await message.bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.video:
                file_id = message.video.file_id
                cap = message.caption + "\n\nСвайпните для ответа👈"
                mesid = await message.bot.send_video(chat_id=id_usr, video=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
                if a.is_prem(id_usr):
                    await message.bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.audio:
                file_id = message.audio.file_id
                cap = message.caption + "\n\nСвайпните для ответа👈"
                mesid = await message.bot.send_audio(chat_id=id_usr, audio=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
                if a.is_prem(id_usr):
                    await message.bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.voice:
                file_id = message.voice.file_id
                cap = message.caption + "\n\nСвайпните для ответа👈"
                mesid = await message.bot.send_voice(chat_id=id_usr, voice=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
                if a.is_prem(id_usr):
                    await message.bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            await message.reply("✅ Сообщение отправлено.", reply_markup=delte_key)
            repli_await[mesid.message_id] = user_id
            delete_mes_usr[user_id] = mesid.message_id
            a.add_send_mes(id_usr)
            a.add_rec_mes(user_id)

@router.callback_query(F.data.startswith("delet_"))
async def delete_mess(callback: CallbackQuery):
    try:
        ref_chat = int(callback.data.split("_")[1])
        await callback.bot.delete_message(chat_id=ref_chat, message_id=delete_mes_usr[callback.from_user.id])
    except Exception:
        await callback.answer("❌Ошибка получения id")
        return
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(text="✅Сообщения удалено")

@router.callback_query(F.data.startswith("writing_"))
async def write_more(callback: CallbackQuery):
    try:
        ref = int(callback.data.split("_")[1])
    except Exception:
        await callback.answer("Ошибка идентификатора.")
        return
    user_referrer[callback.from_user.id] = ref
    mesid = await callback.message.answer(
        "Напишите любое сообщение.\nВы можете отправить текст, видео, фото, аудио и тд.", reply_markup=kb.back_send)
    info_message[callback.from_user.id] = mesid.message_id

@router.callback_query(F.data == "back_sen")
async def send_back(callback: CallbackQuery):
    bots = await callback.bot.get_me()
    await callback.bot.delete_message(chat_id= callback.from_user.id, message_id=callback.message.message_id)
    if callback.from_user.id in user_referrer:
        del user_referrer[callback.from_user.id]
    ref_link = f"https://t.me/{bots.username}?start={callback.from_user.id}"
    await callback.message.answer(
        f"💌Добро пожаловать!\n\n"
        f"📎Ваша  ссылка:\n{ref_link}\n\n"
        f"👥С помощью этой ссылке, люди смогут писать вам анонимные сообщения!!",
    )