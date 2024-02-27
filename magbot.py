import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup
from aiogram.types.web_app_info import WebAppInfo
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods.send_message import SendMessage

from states import *
from db import *
from texts import *


# test - 6748840687:AAEah69Bw4LUvpc43bcGA_Hr19_u98TZiJo
# production - 6565334685:AAFMrkMnbIAB_x8DjHx9494idO8N0qCcoAs
TOKEN = '6565334685:AAFMrkMnbIAB_x8DjHx9494idO8N0qCcoAs'

dp = Dispatcher()


@dp.callback_query(Login.input_login, F.data == "back")
@dp.callback_query(MakeOrder.choose_product, F.data == "back")
@dp.callback_query(TrackOrder.choose_order, F.data == "back")
@dp.callback_query(CheckAvailability.start, F.data == "back")
@dp.callback_query(CheckStatus.start, F.data == "back")
@dp.callback_query(AskQuestion.start, F.data == "back")
@dp.callback_query(CreateAccount.get_name_and_surname,
                   F.data == "back")
async def start_command(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(StartState.start_state)
    kb = InlineKeyboardBuilder()
    kb.adjust(1)

    create_order_button = InlineKeyboardButton(text="Создать заказ", callback_data="create order")
    track_order_button = InlineKeyboardButton(text="Отследить заказ", callback_data="track order")
    get_contacts = InlineKeyboardButton(text="Контакты", callback_data="get contacts")
    check_status = InlineKeyboardButton(text="Узнать статус заказа", callback_data="check status")
    check_availability = InlineKeyboardButton(text="Узнать наличие", callback_data="check availability")
    ask_question = InlineKeyboardButton(text="Задать вопрос", callback_data="ask question")

    authorised_buttons = [create_order_button, track_order_button, check_status, check_availability,
                          ask_question, get_contacts]
    for button in authorised_buttons:
        kb.add(button)

    kb.adjust(1)
    await callback.message.answer(text='Привет, я бот магазина centrmag, выберите желаемое '
                                       'действие', reply_markup=kb.as_markup())


@dp.message(Command('start'))
async def start_command(message: types.Message, state: FSMContext):
    await state.set_state(StartState.start_state)
    kb = InlineKeyboardBuilder()
    kb.adjust(1)

    create_order_button = InlineKeyboardButton(text="Создать заказ", callback_data="create order")
    track_order_button = InlineKeyboardButton(text="Отследить заказ", callback_data="track order")
    get_contacts = InlineKeyboardButton(text="Контакты", callback_data="get contacts")
    check_status = InlineKeyboardButton(text="Узнать статус заказа", callback_data="check status")
    check_availability = InlineKeyboardButton(text="Узнать наличие", callback_data="check availability")
    ask_question = InlineKeyboardButton(text="Задать вопрос", callback_data="ask question")

    authorised_buttons = [create_order_button, track_order_button, check_status, check_availability,
                          ask_question, get_contacts]
    for button in authorised_buttons:
        kb.add(button)

    kb.adjust(1)
    await message.answer(text='Привет, я бот магазина centrmag, выберите желаемое '
                                       'действие', reply_markup=kb.as_markup())


def create_kb():
    kb = InlineKeyboardBuilder()
    cancel_button = InlineKeyboardButton(text="Назад", callback_data=f'back')
    kb.add(cancel_button)
    return kb


@dp.callback_query(F.data == "create account")
async def create_account(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text="Введите свои имя и фамилию через пробел",
                                  reply_markup=kb.as_markup())
    await state.set_state(CreateAccount.get_name_and_surname)


@dp.message(CreateAccount.get_name_and_surname)
async def get_name_and_surname(message: Message, state: FSMContext):
    flag = False
    kb = create_kb()
    try:
        name, surname = message.text.split(' ')
        flag = True
    except Exception as ex:
        print(ex)
        await message.answer(text="Введите два слова: имя и фамилию через пробел",
                             reply_markup=kb.as_markup())
    if flag:
        await state.update_data(name=name)
        await state.update_data(surname=surname)
        await message.answer(text="Введите свою электронную почту", reply_markup=kb.as_markup())
        await state.set_state(CreateAccount.get_email)
    else:
        await state.set_state(CreateAccount.get_name_and_surname)


@dp.callback_query(CreateAccount.get_email, F.data == "back")
async def back_to_name_and_surname(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateAccount.get_name_and_surname)
    kb = create_kb()
    await callback.message.answer(text="Введите свой ИСПРАВЛЕННЫЙ имя и фамилию", reply_markup=kb.as_markup())


@dp.message(CreateAccount.get_email)
async def get_email(message: Message, state: FSMContext):
    print(await state.get_state())
    kb = create_kb()
    await state.update_data(email=message.text)
    await message.answer(text="Введите свой номер телефона", reply_markup=kb.as_markup())
    await state.set_state(CreateAccount.get_phone)


@dp.callback_query(CreateAccount.get_phone, F.data == "back")
async def back_to_email(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateAccount.get_email)
    print(await state.get_state())
    kb = create_kb()
    await callback.message.answer(text="Введите свою ИСПРАВЛЕННУЮ электронную почту", reply_markup=kb.as_markup())


@dp.message(CreateAccount.get_phone)
async def get_phone(message: Message, state: FSMContext):
    kb = create_kb()
    await state.update_data(phone_number=message.text)
    await message.answer(text="Придумайте пароль", reply_markup=kb.as_markup())
    await state.set_state(CreateAccount.get_password)


@dp.callback_query(CreateAccount.get_password, F.data == "back")
async def back_to_phone(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateAccount.get_phone)
    kb = create_kb()
    await callback.message.answer(text="Введите свой ИСПРАВЛЕННЫЙ номер телефона", reply_markup=kb.as_markup())


# @dp.callback_query(F.data == "back", CreateAccount.get_password)
@dp.message(CreateAccount.get_password)
async def get_password(message: Message, state: FSMContext):
    kb = create_kb()
    await state.update_data(password=message.text)
    await message.answer(text="Введите пароль еще раз", reply_markup=kb.as_markup())
    await state.set_state(CreateAccount.get_password_again)


@dp.callback_query(CreateAccount.get_password_again, F.data == "back")
async def back_to_password(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateAccount.get_password)
    kb = create_kb()
    await callback.message.answer(text="Введите свой ИСПРАВЛЕННЫЙ пароль", reply_markup=kb.as_markup())


@dp.callback_query(F.data == "back", CreateAccount.get_password_again)
@dp.message(CreateAccount.get_password_again)
async def get_password_again(message: Message, state: FSMContext):
    data = await state.get_data()
    kb = create_kb()
    password = data['password']
    if message.text != password:
        await message.answer(text="Пароли не совпадают. Попробуйте еще раз",
                             reply_markup=kb.as_markup())
        await state.set_state(CreateAccount.get_password_again)
    else:
        data_list = [data[key] for key in data.keys()]
        data_list.insert(0, message.from_user.id)
        print(data_list)
        register_user(data_list, message.from_user.id)
        await message.answer(text="Аккаунт создан")
        await start_command(message, state)


@dp.callback_query(StartState.start_state, F.data == "login")
async def login(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    if callback.data == "login":
        await callback.message.answer(text="Введите свой email", reply_markup=kb.as_markup())
        await state.set_state(Login.input_login)


@dp.message(Login.input_login)
async def input_login(message: Message, state: FSMContext):
    login = message.text
    kb = create_kb()
    if check_login_in_db(login):
        await state.update_data(login=login)
        await message.answer(text="Введите пароль", reply_markup=kb.as_markup())
        await state.set_state(Login.input_password)
    else:
        await message.answer(text=f"Введенный логин {login} не был найден. Введите еще раз",
                             reply_markup=kb.as_markup())
        await state.set_state(Login.input_login)


@dp.callback_query(Login.input_password, F.data == "back")
async def back_to_input_login(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Login.input_login)
    kb = create_kb()
    await callback.message.answer(text="Введите почту еще раз", reply_markup=kb.as_markup())


@dp.message(Login.input_password)
async def input_password(message: Message, state: FSMContext):
    kb = create_kb()
    entered_password = message.text
    data = await state.get_data()
    login = data['login']
    actual_password = get_password_by_email(login)

    if entered_password != actual_password:
        await message.answer(text="Неверный пароль, попробуйте снова", reply_markup=kb.as_markup())
    else:
        set_authorised(message.from_user.id)
        await message.answer(text="Вход успешный")
        await start_command(message, state)


@dp.callback_query(StartState.start_state, F.data == "get contacts")
async def get_contacts(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    information = """Вот наши контакты:\n\n +7 495 374 67 62

+7 800 707 21 74

info@centrmag.ru

факс: +7 499 713 52 39
Розничный магазин: 125464, Россия, Москва, Пятницкое шоссе, д. 7, к. 1

Время работы:

ПН-ПТ 9:00-19:00"""
    await callback.message.answer(text=information, reply_markup=kb.as_markup())
    await state.set_state(Misc.misc)


@dp.callback_query(StartState.start_state, F.data == "create order")
async def create_order(callback: CallbackQuery, state: FSMContext):
    email, password = get_login_and_password_by_id(callback.from_user.id)
    kb = create_kb()
    kb.add(InlineKeyboardButton(text="Перейти в веб-приложение", web_app=WebAppInfo(url='https://www.centrmag.ru/')))
    await callback.message.answer(text=f"Для оформления заказа вы можете перейти на сайт "
                                       f"https://www.centrmag.ru/\n\nДанные для входа:\nЛогин: {email}\nПароль: "
                                       f"<span class=\"tg-spoiler\">{password}</span>\n\n<i>Для создания <b>тестового</b> заказа введите /order и следуйте инструкциям</i>",
                                  reply_markup=kb.as_markup())
    await state.set_state(MakeOrder.choose_product)


@dp.message(MakeOrder.choose_product, Command("order"))
async def secret_create_order(message: Message, state: FSMContext):
    text = "Доступные товары:\n"
    for i in range(1, 6):
        info = get_info_about_product(i)
        text += f"\n\n{i} {info[1]}, цена: {info[2]}, категория: {info[-1]}"
    await message.answer(text=text)
    await message.answer(
        text="Введите заказ в следующем формате: Товар1(id) - количество1, Товар2(id) - количество2... итд")
    await state.set_state(MakeOrder.create_order)


@dp.message(MakeOrder.create_order)
async def secret_push_order(message: Message, state: FSMContext):
    items = message.text.split(', ')
    order_id = create_order_in_db(message.from_user.id, "paid")
    order_sum = 0
    for item in items:
        product_id, quantity = item.split(' - ')
        price = int(get_product_price_by_id(product_id))
        summa = price * int(quantity)
        order_sum += summa
        insert_order_item(order_id, product_id, quantity, summa)
    push_order_sum(order_id, order_sum)
    await message.answer(text=f"Заказ создан! ID заказа: {order_id}, чтобы посмотреть детали, нажмите на кнопку "
                              f"'Отследить заказы на главном меню'\n\n Нажмите /start")


@dp.callback_query(StartState.start_state, F.data == "track order")
@dp.callback_query(TrackOrder.track_order, F.data == "back")
async def choose_order(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    orders = get_orders_by_chat_id(callback.from_user.id)
    if not orders:
        await state.set_state(TrackOrder.choose_order)
        await callback.message.answer(text="У вас пока нет заказов, вы можете оформить их в разделе 'Создать заказ'",
                                      reply_markup=kb.as_markup())
    else:
        await state.update_data(orders=orders)
        for order in orders:
            order_date = order[1].split(' ')[0]
            order_button = InlineKeyboardButton(text=f"№{order[0]} от {order_date} на сумму {order[-1]} руб",
                                                callback_data=f"order: {order[0]}")
            kb.add(order_button)
        kb.adjust(1)
        await callback.message.answer(text="Выберите заказ из предложенного снизу или введите номер заказа",
                                      reply_markup=kb.as_markup())
        await state.set_state(TrackOrder.choose_order)


@dp.callback_query(TrackOrder.choose_order)
async def track_order(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    order_id = int(callback.data.split(': ')[1])
    order_info = get_info_about_order(order_id)
    order_statuses = {"new": "Новый", "paid": "Оплаченный"}
    text = f"Заказ № {order_id}\nДата: {order_info[1]}\nСтатус: {order_statuses[order_info[2]]}\nСумма заказа: {order_info[-1]} руб\n\nДетали:\n\n"

    order_items = get_items_by_order_id(order_id)
    for item in order_items:
        item_name, item_quantity, item_summa = item
        text += f"Товар: {item_name}\nКоличество: {item_quantity}\nИтого за товар: {item_summa} руб\n\n"

    await callback.message.answer(text=text, reply_markup=kb.as_markup())
    await state.set_state(TrackOrder.track_order)


@dp.message(TrackOrder.choose_order)
async def m_choose_order(message: Message, state: FSMContext):
    order_id = int(message.text)
    data = await state.get_data()
    flag = False
    for order in data['orders']:
        if order_id == order[0]:
            flag = True
            break
    if not flag:
        await message.answer(text=f"Заказа с номером {order_id} нет, попробуйте еще раз")
        await state.set_state(TrackOrder.choose_order)
    else:
        await state.update_data(order_id=order_id)
        await state.set_state(TrackOrder.track_order)
        await m_track_order(message, state)


@dp.message(TrackOrder.track_order)
async def m_track_order(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data['order_id']
    kb = create_kb()
    order_info = get_info_about_order(order_id)
    order_statuses = {"new": "Новый", "paid": "Оплаченный"}
    text = f"Заказ № {order_id}\nДата: {order_info[1]}\nСтатус: {order_statuses[order_info[2]]}\nСумма заказа: {order_info[-1]} руб\n\nДетали:\n\n"

    order_items = get_items_by_order_id(order_id)
    for item in order_items:
        item_name, item_quantity, item_summa = item
        text += f"Товар: {item_name}\nКоличество: {item_quantity}\nИтого за товар: {item_summa} руб\n\n"

    await message.answer(text=text, reply_markup=kb.as_markup())
    await state.set_state(TrackOrder.track_order)


@dp.callback_query(F.data == "logout")
async def logout(callback: CallbackQuery, state: FSMContext):
    yes_button = KeyboardButton(text='Да')
    cancel_button = KeyboardButton(text='Отмена')
    btns = [[yes_button], [cancel_button]]
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=btns)
    await callback.message.answer("Вы точно хотите выйти из аккаунта?", reply_markup=kb)
    await state.set_state(Logout.confirm_logout)


@dp.message(Logout.confirm_logout)
async def choose_quantity(message: Message, state: FSMContext):
    if message.text == "Да":
        set_unauthorised(message.from_user.id)
        await message.answer('Выход успешный', reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer('Выход отменен', reply_markup=types.ReplyKeyboardRemove())
    await start_command(message, state)


@dp.callback_query(F.data == "check status")
async def check_status(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    order_number = InlineKeyboardButton(text="Указать номер заказа", callback_data="input order number")
    fio = InlineKeyboardButton(text="Указать ФИО", callback_data="input fio")
    kb.add(order_number)
    kb.add(fio)
    kb.adjust(1)
    await callback.message.answer(text="Укажите номер заказа или ФИО, на кого оформлен заказ",
                                  reply_markup=kb.as_markup())
    await state.set_state(CheckStatus.start)


@dp.callback_query(CheckStatus.input_order_number, F.data == "back")
async def back_to_check_status(callback: CallbackQuery, state: FSMContext):
    await check_status(callback, state)


@dp.callback_query(CheckStatus.input_fio, F.data == "back")
async def back_to_check_status(callback: CallbackQuery, state: FSMContext):
    await check_status(callback, state)


@dp.callback_query(F.data == "input order number")
async def input_order_number(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer("Введите номер заказа", reply_markup=kb.as_markup())
    await state.set_state(CheckStatus.input_order_number)


@dp.callback_query(F.data == "input fio")
async def input_fio(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer("Введите ФИО", reply_markup=kb.as_markup())
    await state.set_state(CheckStatus.input_fio)


@dp.callback_query(F.data == "check availability")
async def check_availability(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer("Введите артикул товара", reply_markup=kb.as_markup())
    await state.set_state(CheckAvailability.start)


@dp.callback_query(F.data == "how to search")
async def how_to_search(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    buttons = [
        InlineKeyboardButton(text="Быстрый поиск по наименованию товара", callback_data="quick search by name"),
        InlineKeyboardButton(text="Поиск по наименованию товара", callback_data="search by name"),
        InlineKeyboardButton(text="Быстрый поиск по артикулу товара", callback_data="quick search by vendor"),
        InlineKeyboardButton(text="Поиск по артикулу товара", callback_data="search by vendor"),
        InlineKeyboardButton(text="Поиск по автору книги", callback_data="search by author"),
        InlineKeyboardButton(text="Поиск по ISBN", callback_data="search by isbn")]
    for button in buttons:
        kb.add(button)
    kb.adjust(1)

    await callback.message.answer("О том, как искать товар можно ознакомиться на сайте: "
                                  "https://www.centrmag.ru/information_pages/poisk/\n\nТакже вы можете посмотреть, "
                                  "как искать товар по способам поиска, нажав на соответствующую кнопку",
                                  reply_markup=kb.as_markup())
    await state.set_state(Misc.misc)


@dp.callback_query(HowToSearch.how_to_search)
async def back_to_how_to_search(callback: CallbackQuery, state: FSMContext):
    await how_to_search(callback, state)


@dp.callback_query(F.data == "quick search by name")
async def quick_search_by_name(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer_photo(photo="https://www.centrmag.ru/img/help_01.png",
                                        caption=quick_search_by_name_text,
                                        reply_markup=kb.as_markup())
    await state.set_state(HowToSearch.how_to_search)


@dp.callback_query(F.data == "search by name")
async def quick_search_by_name(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer_photo(photo="https://www.centrmag.ru/img/help_02.png",
                                        caption=search_by_name_text,
                                        reply_markup=kb.as_markup())
    await state.set_state(HowToSearch.how_to_search)


@dp.callback_query(F.data == "quick search by vendor")
async def quick_search_by_name(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer_photo(photo="https://www.centrmag.ru/img/help_01_.png",
                                        caption=quick_search_by_vendor_text,
                                        reply_markup=kb.as_markup())
    await state.set_state(HowToSearch.how_to_search)


@dp.callback_query(F.data == "search by vendor")
async def quick_search_by_name(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer_photo(photo="https://www.centrmag.ru/img/help_02_.png",
                                        caption=search_by_vendor_text,
                                        reply_markup=kb.as_markup())
    await state.set_state(HowToSearch.how_to_search)


@dp.callback_query(F.data == "search by author")
async def quick_search_by_name(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer_photo(photo="https://www.centrmag.ru/img/help_03.png",
                                        caption=search_by_author_text,
                                        reply_markup=kb.as_markup())
    await state.set_state(HowToSearch.how_to_search)


@dp.callback_query(F.data == "search by isbn")
async def quick_search_by_name(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer_photo(photo="https://www.centrmag.ru/img/help_03.png",
                                        caption=search_by_isbn_text,
                                        reply_markup=kb.as_markup())
    await state.set_state(HowToSearch.how_to_search)


@dp.callback_query(F.data == "grafik raboty")
async def grafik_raboty(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=grafik_raboty_text, parse_mode=ParseMode.HTML, reply_markup=kb.as_markup())
    await state.set_state(Misc.misc)


@dp.callback_query(F.data == "how to get")
async def how_to_get(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    buttons = [
        InlineKeyboardButton(text="От станции метро Волоколамская", callback_data="from metro"),
        InlineKeyboardButton(text="От станции МЦД-2 Волоколамская", callback_data="from mcd"),
        InlineKeyboardButton(text="Доехать на автобусе", callback_data="by bus")]
    for button in buttons:
        kb.add(button)
    kb.adjust(1)
    await callback.message.answer_photo(photo="https://imgur.com/a/5FSxMfP", reply_markup=kb.as_markup())
    await state.set_state(Misc.misc)


@dp.callback_query(HowToGet.how_to_get)
async def back_to_how_to_get(callback: CallbackQuery, state: FSMContext):
    await how_to_get(callback, state)


@dp.callback_query(F.data == "from metro")
async def from_metro(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=from_metro_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await state.set_state(HowToGet.how_to_get)


@dp.callback_query(F.data == "from mcd")
async def from_mcd(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=from_mcd_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await state.set_state(HowToGet.how_to_get)


@dp.callback_query(F.data == "by bus")
async def by_bus(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=by_bus_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await state.set_state(HowToGet.how_to_get)


@dp.callback_query(F.data == "delivery methods")
async def delivery_methods(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    for i, method in enumerate(delivery_methods_list):
        kb.add(InlineKeyboardButton(text=method, callback_data=str(i)))
    kb.adjust(1)
    await callback.message.answer(text=delivery_methods_text, parse_mode=ParseMode.HTML, reply_markup=kb.as_markup())
    await state.set_state(DeliveryMethods.delivery_methods)


@dp.callback_query(DeliveryMethods.method, F.data == "back")
async def back_to_delivery_methods(callback: CallbackQuery, state: FSMContext):
    await delivery_methods(callback, state)


@dp.callback_query(DeliveryMethods.delivery_methods, F.data == "0")
async def samovivoz(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=samovivoz_text, reply_markup=kb.as_markup())
    await state.set_state(DeliveryMethods.method)


@dp.callback_query(DeliveryMethods.delivery_methods, F.data == "1")
async def pvz_i_postamaty(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer_photo(photo='https://imgur.com/a/LRsILZY', caption=pvz_text, reply_markup=kb.as_markup())
    await state.set_state(DeliveryMethods.method)


@dp.callback_query(DeliveryMethods.delivery_methods, F.data == "2")
async def kurierskaya(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer_photo(photo='https://imgur.com/a/40UlmiC')
    await callback.message.answer(text=kurierskaya_text, reply_markup=kb.as_markup())
    await state.set_state(DeliveryMethods.method)


@dp.callback_query(DeliveryMethods.delivery_methods, F.data == "3")
async def beskontaktnaya_kurierskaya(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=beskontaktnaya_kurierskaya_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await state.set_state(DeliveryMethods.method)


@dp.callback_query(DeliveryMethods.delivery_methods, F.data == "4")
async def punkti_samovivoza(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=punkti_samovivoza_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await state.set_state(DeliveryMethods.method)


@dp.callback_query(DeliveryMethods.delivery_methods, F.data == "5")
async def kurierskaya_po_vsei_rossii(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=kurierskaya_po_vsei_rossii_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await state.set_state(DeliveryMethods.method)


@dp.callback_query(DeliveryMethods.delivery_methods, F.data == "6")
async def po_pochte(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=po_pochte_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML, )
    await state.set_state(DeliveryMethods.method)


@dp.callback_query(F.data == "payment methods")
async def payment_methods(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    for i, method in enumerate(payment_methods_list):
        kb.add(InlineKeyboardButton(text=method, callback_data=str(i)))
    kb.adjust(1)
    await callback.message.answer(text=payment_methods_text, reply_markup=kb.as_markup())
    await state.set_state(PaymentMethods.payment_methods)


@dp.callback_query(PaymentMethods.method, F.data == "back")
async def back_to_payment_methods(callback: CallbackQuery, state: FSMContext):
    await payment_methods(callback, state)


@dp.callback_query(PaymentMethods.payment_methods, F.data == "0")
async def cash_payment(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=cash_payment_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML, )
    await state.set_state(PaymentMethods.method)


@dp.callback_query(PaymentMethods.payment_methods, F.data == "1")
async def cashless_payment(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=cashless_payment_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML, )
    await state.set_state(PaymentMethods.method)


@dp.callback_query(PaymentMethods.payment_methods, F.data == "2")
async def transfer_to_bank_card(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=transfer_to_bank_card_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML, )
    await state.set_state(PaymentMethods.method)


@dp.callback_query(PaymentMethods.payment_methods, F.data == "3")
async def transfer_to_e_wallet_card(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=transfer_to_e_wallet_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML, )
    await state.set_state(PaymentMethods.method)


@dp.callback_query(PaymentMethods.payment_methods, F.data == "4")
async def money_transfer_systems(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=money_transfer_systems_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML, )
    await state.set_state(PaymentMethods.method)


@dp.callback_query(PaymentMethods.payment_methods, F.data == "5")
async def payment_terminal(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=payment_terminal_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML, )
    await state.set_state(PaymentMethods.method)


@dp.callback_query(F.data == "ask question")
@dp.callback_query(Misc.misc, F.data == "back")
@dp.callback_query(DeliveryMethods.delivery_methods, F.data == "back")
@dp.callback_query(PaymentMethods.payment_methods, F.data == "back")
async def ask_question_start(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    kb.add(
        InlineKeyboardButton(text="Как отследить заказ", callback_data="how to order"),
        InlineKeyboardButton(text="Как найти товар", callback_data="how to search"),
        InlineKeyboardButton(text="Как выбрать нужный журнал", callback_data="how to choose magazine"),
        InlineKeyboardButton(text="Какая стоимость журнала", callback_data="price of magazine"),
        InlineKeyboardButton(text="Способы оплаты", callback_data="payment methods"),
        InlineKeyboardButton(text="График работы / Адрес", callback_data="grafik raboty"),
        InlineKeyboardButton(text="Как добраться", callback_data="how to get"),
        InlineKeyboardButton(text="Способы доставки", callback_data="delivery methods"),
        InlineKeyboardButton(text="Задать другой вопрос", callback_data="ask another question"),
    )
    kb.adjust(1)
    await callback.message.answer(text="Выберите интересующую тему", reply_markup=kb.as_markup())
    await state.set_state(AskQuestion.start)


@dp.callback_query(F.data == "how to order")
async def how_to_order_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="В разработке")
    # TODO


@dp.callback_query(F.data == "how to choose magazine")
async def how_to_choose_magazine(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="В разработке")
    # TODO



async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
