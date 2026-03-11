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
from app.states import idea, Premium, StaticState
from datetime import datetime
from dateutil.relativedelta import relativedelta

router = Router()

user_referrer = {}
idPremUsr = []
awaiting_replay = {}
info_message = {}
replay_id = {}
delete_mes_usr = {}
repli_await = {}

@router.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    args = command.args
    a.ensure_user_exists(message.from_user.id)
    user = message.from_user
    user_id = user.id
    if a.is_prem(user_id):
        enddb = a.get_date(user_id)
        end = datetime.fromisoformat(enddb[0])
        if datetime.now() < end:
            a.del_prem(user_id)
    if args:
        try:
            referrer_id = int(args)
            await message.delete()
            await state.update_data(refer = user_id)
            isd = await state.get_data()
            a.add_ref(isd["refer"])
            await state.clear()
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
    get_prem = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Дать премиум", callback_data=f"getprem_{shared}")],
        [InlineKeyboardButton(text="Снять премиум", callback_data=f"delprem_{shared}")]
    ])
    chat = await bot.get_chat(shared)
    try:
        first_name = chat.first_name
        username = chat.username or "None"
    except Exception:
        first_name = " "
        username = None
        await message.answer("❌Пользователя невозможно добавить, так как он еще ни разу не писал боту")
    if a.is_admin(message.from_user.id):
        endbd = 0
        date = 0
        if a.is_prem(shared):
            endbd = a.get_date(shared)
            end = datetime.fromisoformat(endbd[0])
            date = end.strftime("%d.%m.%Y %H:%M")
        text = f"\nПремиум активен до {date}" if a.is_prem(shared) else "Премиум не активен"
        await message.answer(f"Пользователь <code>{chat.id}</code>, {chat.username or ' '}<code>\n{text}</code>", reply_markup=get_prem, parse_mode="HTML")

@router.message(Command("setprem"))
async def add_preimum(message:Message, command: CommandObject, state: FSMContext):
    user_id, time, date= command.args.split(" ", maxsplit=2)
    idu = 0
    username = 0
    first = 0
    if not command.args:
        await message.answer("Вы ввели неверные данные")
    if command.args:
        try:
            user_id = int(user_id)
            if a.is_prem(user_id):
                await message.answer("Пользователь уже премиум")
                return
            time = int(time)
            chat = await message.bot.get_chat(user_id)
            try:
                idu = chat.id
                username = chat.username
                first = chat.first_name
                await state.update_data(id_state = idu, first_state = first, username_state = username)
            except Exception:
                await message.answer("❌Пользователя невозможно добавить, так как он еще ни разу не писал боту")
                return
        except ValueError:
            await message.answer("Неверно введено айдт или дата")
        if date == "м":
            user = {
                "start": datetime.now()
            }
            user["end"] = user["start"] + relativedelta(months=time)
            info = await state.get_data()
            a.add_premium(info["id_state"], info["first_state"], info["username_state"])
            a.add_date(user_id, user["end"])
            await message.bot.send_message(chat_id=idu, text=f"Поздравляем, вы стали обладателем премиума!"
                                                             f'\n\nПодписка действует до {user["end"].strftime("%d.%m.%Y %H:%M")}')
            await message.answer("Премиум успешно выдан")
        if date == "д":
            user = {
                "start": datetime.now()
            }
            user["end"] = user["start"] + relativedelta(days=time)
            info = await state.get_data()
            a.add_premium(info["id_state"], info["first_state"], info["username_state"])
            a.add_date(user_id, user["end"])
            await message.bot.send_message(chat_id=idu, text = f"Поздравляем, вы стали обладателем премиума!"
                                                               f'\n\nПодписка действует до {user["end"].strftime("%d.%m.%Y %H:%M")}')
            await message.answer("Премиум успешно выдан")

@router.message(Command("idea"))
async def idea_usr(message: Message, state: FSMContext):
    await state.set_state(idea.idea_text)
    await message.answer("Напишите о том, как бы вы улучшили бота:", reply_markup=kb.back_send)

@router.message(idea.idea_text)
async def add_text_idea(message: Message, state: FSMContext):
    if message.text:
        id_admin = a.get_id_admin()
        for admin in id_admin:
            await message.bot.send_message(chat_id=admin, text = f"Пользователь {message.from_user.id} {message.from_user.username} Предлагает"
                                                                 f"\n\n<blockquote>{message.text}</blockquote>\n", parse_mode="HTML")
    await state.clear()

@router.message(Command("premiumus"))
async def all_admins(message: Message):
    text = f"Все премиум-пользователи бота: \n\n"
    if a.is_admin(message.from_user.id):
        premiums = a.get_premium()
        for premium in premiums:
            ida, first, username = premium[:3]
            print(premium)
            text += f"Id: <code>{ida}</code>\n"
            text += f"Имя: {first}\n"
            text += f"Юзернейм: @{username}\n\n"
        await message.answer(text + f"\nДля того чтобы дать премиум, воспользуйтесь кнопкой Добавить премиум"
                                    f"\n\nДля анулирования премиума, используйте команду /delprem (id пользователя, которого хотите удалить)"
                                    f"\n\nЧтобы дать преиум пользователю, вы можете: "
                                    f"\nИспользовать команду /setprem id-пользователя колисчетсво(дней/месяцев) д или м"
                                    f"\nПрислать боту контакт и присвоить премиум по кнопке",
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
            await message.bot.send_message(chat_id=id_us, text = "❌Вы больше не премиум пользователь")
            await message.answer("✅Вы успешно сняли премиум с пользователя")
        except ValueError:
            await message.answer("❌ОШИБКА. ID передан неверено")
    else:
        await message.answer("❌Вы не передали id пользователя")

@router.message(Premium.add_premka)
async def state_prem(message: Message, state: FSMContext):
    await message.answer("Премиум успешно выдан")
    days1 = 0
    try:
        days1 = int(message.text)
    except ValueError:
        await message.answer("Количество должно быть числовым значением!")
        await state.set_state(Premium.add_premka)
        return
    user = {"start": datetime.now()}
    user["end"] = user["start"] + relativedelta(days = days1)
    data = await state.get_data()
    a.add_premium(data["id_state"], data["first_state"], data["username_state"])
    a.add_date(data["id_state"], user["end"])
    await message.answer(f"✅Премиум успешно выдан, преимум продлиться до `{user["end"]}`", parse_mode="Markdown")
    dat = user["end"]
    await message.bot.send_message(chat_id=data["id_state"], text=f"✅Вы стали премиум пользователем, ваша подписка продлиться до `{dat.strftime('%d.%m.%Y %H:%M')}`", parse_mode="MarkdownV2")
    await state.clear()

@router.message()
async def forward_to_referrer(message: Message, state: FSMContext):
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
                cap = message.caption or " "
                mesid = await message.bot.send_photo(chat_id=referrer_id, photo=file_id, caption=cap)
                if a.is_prem(referrer_id):
                    await message.bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.video:
                file_id = message.video.file_id
                cap = message.caption or " "
                mesid = await message.bot.send_video(chat_id=referrer_id, video=file_id, caption= cap)
                if a.is_prem(referrer_id):
                    await message.bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.audio:
                file_id =message.audio.file_id
                cap = message.caption or " "
                mesid = await message.bot.send_audio(chat_id=referrer_id, audio=file_id, caption=cap)
                if a.is_prem(referrer_id):
                    await message.bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.voice:
                file_id = message.voice.file_id
                cap = message.caption or " "
                mesid = await message.bot.send_voice(chat_id=referrer_id, voice=file_id, caption=cap)
                if a.is_prem(referrer_id):
                    await message.bot.send_message(chat_id=referrer_id, text = f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            await message.reply("✅ Сообщение отправлено.", reply_markup=delte_key)
            await message.answer(
                f"💌Здесь вы можете получать анонимные сообщения!!\n\n"
                f"📎 Ваша  ссылка:\n{ref_link}\n\n"
                f"👥C помощью этой ссылке, люди смогут писать вам анонимные сообщения!!", reply_markup=send_url
            )
            await state.update_data(userid = user_id, referid = referrer_id)
            data = await state.get_data()
            a.add_rec_mes(data["referid"])
            a.add_send_mes(data["userid"])
            await state.clear()
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
                cap = message.caption or " "
                mesid = await message.bot.send_photo(chat_id=id_usr, photo=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}"
                                             )
                if a.is_prem(id_usr):
                    await message.bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.video:
                file_id = message.video.file_id
                cap = message.caption or " "
                mesid = await message.bot.send_video(chat_id=id_usr, video=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
                if a.is_prem(id_usr):
                    await message.bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.audio:
                file_id = message.audio.file_id
                cap = message.caption or " "
                mesid = await message.bot.send_audio(chat_id=id_usr, audio=file_id,
                                             caption=f"📩 Вам ответили на ваше сообщение:\n\n{cap}")
                if a.is_prem(id_usr):
                    await message.bot.send_message(chat_id=id_usr,
                                           text=f"Юзер @{message.from_user.username}\nid = {message.from_user.first_name}\nимя = {message.from_user.id}")
            elif message.voice:
                file_id = message.voice.file_id
                cap = message.caption or " "
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

@router.callback_query(F.data.startswith("getprem_"))
async def prem_add(callback: CallbackQuery, state:FSMContext):
    user_id = 0
    try:
        user_id = int(callback.data.split("_")[1])
    except ValueError:
        await callback.message.answer("Произошла ошибка..")
        return
    cht = await callback.bot.get_chat(user_id)
    await state.update_data(id_state = user_id, first_state = cht.first_name, username_state = cht.username)
    await state.set_state(Premium.add_premka)
    await callback.message.answer("Введите срок премиума(в днях)")
    await callback.answer()

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