import asyncio
import datetime
import logging
import re
import sys
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.methods import send_photo
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup
from aiogram.types.web_app_info import WebAppInfo
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods.send_message import SendMessage

from openai_api import get_openai_response
from states import *
from db_old import *
from db import *
from texts import *

# test - 6748840687:AAEah69Bw4LUvpc43bcGA_Hr19_u98TZiJo
# production - 6565334685:AAFMrkMnbIAB_x8DjHx9494idO8N0qCcoAs
TOKEN = '6565334685:AAFMrkMnbIAB_x8DjHx9494idO8N0qCcoAs'

dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


def check_auth(data, kb):
    if not data['user_auth']:
        auth_button = InlineKeyboardButton(text="Авторизоваться", callback_data="auth")
        reg_button = InlineKeyboardButton(text="Зарегистрироваться", callback_data="register")
        kb.add(auth_button, reg_button)
        kb.adjust(1)
        return False
    else:
        return True


@dp.callback_query(Login.input_login, F.data == "back")
@dp.callback_query(MakeOrder.choose_product, F.data == "back")
@dp.callback_query(TrackOrder.choose_order, F.data == "back")
@dp.callback_query(CheckAvailability.start, F.data == "back")
@dp.callback_query(Cart.start, F.data == "back")
@dp.callback_query(CheckStatus.start, F.data == "back")
@dp.callback_query(AskQuestion.start, F.data == "back")
@dp.callback_query(Auth.input_password, F.data == "back")
@dp.callback_query(Cart.pay, F.data == "back")
@dp.callback_query(CreateAccount.get_name_and_surname,
                   F.data == "back")
async def start_command(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    kb = InlineKeyboardBuilder()
    try:
        print(data['user_cart'])
        print(data['user_auth'])
        check_auth(data, kb)
    except Exception as ex:
        print("Создал новую корзину")
        await state.update_data(user_cart=[])
        await state.update_data(user_auth=False)
        auth_button = InlineKeyboardButton(text="Авторизоваться", callback_data="auth")
        reg_button = InlineKeyboardButton(text="Зарегистрироваться", callback_data="register")
        kb.add(auth_button, reg_button)
        kb.adjust(1)


    await state.set_state(StartState.start_state)

    kb.adjust(1)

    create_order_button = InlineKeyboardButton(text="Посмотреть каталог", callback_data="create order")
    get_contacts = InlineKeyboardButton(text="Контакты", callback_data="get contacts")
    check_status = InlineKeyboardButton(text="Узнать статус заказа", callback_data="check status")
    check_availability = InlineKeyboardButton(text="Узнать наличие", callback_data="check availability")
    cart = InlineKeyboardButton(text="Корзина", callback_data="cart")
    ask_question = InlineKeyboardButton(text="Задать вопрос", callback_data="ask question")

    authorised_buttons = [create_order_button, check_status, check_availability, cart,
                          ask_question, get_contacts, ]
    for button in authorised_buttons:
        kb.add(button)
    kb.adjust(1)
    await callback.message.answer(text='Привет, я бот магазина centrmag, выберите желаемое '
                                       'действие', reply_markup=kb.as_markup())


@dp.message(Command('start'))
async def start_command(message: types.Message, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.adjust(1)
    data = await state.get_data()
    try:
        print(data['user_cart'])
        print(data['user_auth'])
        check_auth(data, kb)
    except Exception as ex:
        print("Создал новую корзину")
        await state.update_data(user_cart=[])
        await state.update_data(user_auth=False)
        auth_button = InlineKeyboardButton(text="Авторизоваться", callback_data="auth")
        reg_button = InlineKeyboardButton(text="Зарегистрироваться", callback_data="register")
        kb.add(auth_button, reg_button)
        kb.adjust(1)

    await state.set_state(StartState.start_state)

    create_order_button = InlineKeyboardButton(text="Посмотреть каталог", callback_data="create order")
    get_contacts = InlineKeyboardButton(text="Контакты", callback_data="get contacts")
    check_status = InlineKeyboardButton(text="Узнать статус заказа", callback_data="check status")
    check_availability = InlineKeyboardButton(text="Узнать наличие", callback_data="check availability")
    cart = InlineKeyboardButton(text="Корзина", callback_data="cart")
    ask_question = InlineKeyboardButton(text="Задать вопрос", callback_data="ask question")

    authorised_buttons = [create_order_button, check_status, check_availability, cart,
                          ask_question, get_contacts]

    for button in authorised_buttons:
        kb.add(button)

    kb.adjust(1)
    await message.answer(text='Привет, я бот магазина centrmag, выберите желаемое '
                              'действие', reply_markup=kb.as_markup())


def create_kb(button_name="Назад"):
    kb = InlineKeyboardBuilder()
    cancel_button = InlineKeyboardButton(text=button_name, callback_data=f'back')
    kb.add(cancel_button)
    return kb


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
    email, password = "email", "password"
    kb = create_kb()
    kb.add(InlineKeyboardButton(text="Перейти в веб-приложение", web_app=WebAppInfo(url='https://www.centrmag.ru/')))
    await callback.message.answer(text=f"Для оформления заказа вы можете перейти на сайт "
                                       f"https://www.centrmag.ru/\n\nДанные для входа:\nЛогин: {email}\nПароль: "
                                       f"<span class=\"tg-spoiler\">{password}</span>\n\n",
                                  reply_markup=kb.as_markup())
    await state.set_state(MakeOrder.choose_product)


@dp.callback_query(CheckStatus.choose_order, F.data == "back")
@dp.callback_query(F.data == "check status")
async def check_status_start(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    data = await state.get_data()
    if not check_auth(data, kb):
        text = "Чтобы узнать статус заказа необходимо авторизоваться"
    else:
        text = "Выберите заказ из списка ниже"
        orders = select_orders_by_email(data['email'])
        print(orders)
        await state.update_data(orders=orders)
        for order in orders:
            button_text = ""
            order_id = order['order_id']
            button_text += str(order_id)
            button_text += '. '
            button_text += order['data']
            button_text += ' '
            button_text += order['time']
            kb.add(InlineKeyboardButton(text=button_text, callback_data=f"order|{order_id}"))
        kb.adjust(1)
    await callback.message.answer(text=text,
                                  reply_markup=kb.as_markup())
    await state.set_state(CheckStatus.start)


@dp.callback_query(CheckStatus.start)
async def check_status_choose_order(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    order_id = callback.data.split('|')[1]
    data = await state.get_data()
    orders = data['orders']
    order = find_order_by_id(order_id, orders)
    order_details = get_order_details_as_string(order)

    await callback.message.answer(text=order_details, reply_markup=kb.as_markup())
    await state.set_state(CheckStatus.choose_order)


def find_order_by_id(order_id, orders_list):
    for order in orders_list:
        if order['order_id'] == int(order_id):
            return order
    return None


def get_order_details_as_string(order):
    order_info = f"<b>Информация о заказе №{order['order_id']}</b>: \n"
    order_info += f"<b>Статус</b>: Новый\n"
    order_info += f"<b>Дата</b>: {order['data']}\n"
    order_info += f"<b>Время</b>: {order['time']}\n"
    order_info += f"<b>Адрес</b>: г. {order['city']}, ул. {order['street']} {order['home']}\n"
    order_info += "<b>Товары в заказе</b>:\n"
    order_info += "-------------------------\n"
    total_sum = 0  # Инициализация переменной для подсчета итоговой суммы
    for item in order['zakaz']:
        order_info += f"- <b>Наименование</b>: {item['item_name']}\n"
        order_info += f"  <b>Артикул</b>: {item['item_id']}\n"
        order_info += f"  <b>Количество</b>: {item['quantity']}\n"
        order_info += f"  <b>Сумма</b>: {item['summa']} руб.\n"
        total_sum += int(item['summa'])  # Добавление суммы товара к общей сумме
        order_info += "-------------------------\n"
    order_info += f"<b>Итого</b>: {total_sum} руб.\n"  # Добавление информации об итоговой сумме
    return order_info





@dp.callback_query(F.data == "register")
async def check_status_input_fio(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Введите свои ФИО")
    await state.set_state(CheckStatus.input_fio)


@dp.message(CheckStatus.input_fio)
async def check_status_input_email(message: Message, state: FSMContext):
    if not all(char.isalpha() or char.isspace() for char in message.text):
        await message.answer(text="Некорректный ввод введите ФИО еще раз")
    else:
        await state.update_data(fio=message.text)
        await message.answer(text="Введите электронную почту")
        await state.set_state(CheckStatus.input_email)


def is_valid_email(email):
    # Регулярное выражение для проверки email
    pattern = r'^[\w\.-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@dp.message(CheckStatus.input_email)
async def check_status_input_email(message: Message, state: FSMContext):
    if not is_valid_email(message.text):
        await message.answer(text="Некорректный ввод почты, попробуйте еще раз")
    else:
        await state.update_data(email=message.text)
        await message.answer(text="Введите пароль")
        await state.set_state(CheckStatus.input_password)


@dp.message(CheckStatus.input_password)
async def check_status_input_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer(text="Повторите пароль")
    await state.set_state(CheckStatus.repeat_password)


@dp.message(CheckStatus.repeat_password)
async def check_status_repeat_password(message: Message, state: FSMContext):
    kb = create_kb()
    kb.add(
        InlineKeyboardButton(text="Авторизоваться", callback_data="auth")
    )
    kb.adjust(1)
    data = await state.get_data()
    password = data['password']
    if password != message.text:
        await message.answer(text="Пароли не совпадают, попробуйте еще раз")
    else:
        fio = data['fio']
        email = data['email']
        user_id = message.from_user.id
        username = message.from_user.username
        if register_user(user_id, username, password, fio, email):
            await message.answer(text="Аккаунт создан, можете авторизоваться", reply_markup=kb.as_markup())
        else:
            await message.answer(text="Произошла ошибка")


@dp.callback_query(F.data == "auth")
async def auth_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Введите свой email")
    await state.set_state(Auth.input_email)


@dp.message(Auth.input_email)
async def auth_start(message: Message, state: FSMContext):
    email = message.text
    if check_user_in_db(email):
        await message.answer(text="Введите пароль")
        await state.update_data(email=email)
        await state.set_state(Auth.input_password)
    else:
        await message.answer(text="Пользователь с таким email не найден")


@dp.message(Auth.input_password)
async def auth_input_password(message: Message, state: FSMContext):
    kb = create_kb("На главную")
    data = await state.get_data()
    email = data['email']
    password = message.text
    if check_password(email, password):
        await message.answer(text="Успешная авторизация", reply_markup=kb.as_markup())
        await state.update_data(user_auth=True)
        await state.update_data(email=email)
    else:
        await message.answer(text="Неверный пароль, попробуйте еще раз")


@dp.callback_query(F.data == "check availability")
@dp.callback_query(CheckAvailability.choose_quantity, F.data == "resume searching")
@dp.callback_query(CheckAvailability.pzc, F.data == "back")
async def check_availability_start(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer("Введите название товара", reply_markup=kb.as_markup())
    await state.set_state(CheckAvailability.start)


@dp.message(CheckAvailability.start)
async def check_availability_send_results(message: Message, state: FSMContext):
    kb = create_kb()
    item_name = message.text
    await state.update_data(item_name=item_name)
    res, stocks = get_stocks(item_name)
    print(f'stocks: {stocks}')
    await state.set_state(CheckAvailability.pzc)
    if stocks is not None:
        if stocks > 0:
            caption = f"Товар <b>{res['ogl']}</b>\nИмеется в количестве <b>{stocks} шт.</b>\nЦена: <b>{res['cena']} рублей за шт.</b>"
            kb.add(
                InlineKeyboardButton(text="Добавить в корзину",
                                     callback_data=f"add to cart|{res['Id']}|{stocks}|{res['cena']}")
            )
            kb.adjust(1)
        else:
            caption = f"В данный момент товара <b>{res['ogl']}</b> на складе нет"
        try:
            await bot.send_photo(chat_id=message.from_user.id,
                                 photo=f'https://www.centrmag.ru/catalog/{res["obl"]}',
                                 caption=caption,
                                 reply_markup=kb.as_markup())
        except Exception as ex:
            print(ex)
            await message.answer(text=caption,
                                 reply_markup=kb.as_markup())
    else:
        await message.answer(text="Товар не найден, попробуйте ввести название еще раз", reply_markup=kb.as_markup())


@dp.callback_query(CheckAvailability.add_to_cart, F.data == "back")
async def check_availability_back_to_send_results(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    data = await state.get_data()
    item_name = data['item_name']
    res, stocks = get_stocks(item_name)
    print(f'stocks: {stocks}')
    await state.set_state(CheckAvailability.pzc)
    if stocks is not None:
        if stocks > 0:
            caption = f"Товар <b>{res['ogl']}</b>\nИмеется в количестве <b>{stocks} шт.</b>\nЦена: <b>{res['cena']} рублей за шт.</b>"
            kb.add(
                InlineKeyboardButton(text="Добавить в корзину",
                                     callback_data=f"add to cart|{res['Id']}|{stocks}|{res['cena']}")
            )
            kb.adjust(1)
        else:
            caption = f"В данный момент товара <b>{res['ogl']}</b> на складе нет"
        try:
            print(f"yooooooo {callback.message.from_user.id}")
            await bot.send_photo(chat_id=callback.message.from_user.id,
                                 photo=f'https://www.centrmag.ru/catalog/{res["obl"]}',
                                 caption=caption,
                                 reply_markup=kb.as_markup())
        except Exception as ex:
            print(ex)
            await callback.message.answer(text=caption,
                                 reply_markup=kb.as_markup())
    else:
        await callback.message.answer(text="Товар не найден, попробуйте ввести название еще раз", reply_markup=kb.as_markup())


@dp.callback_query(CheckAvailability.pzc, F.data.startswith("add to cart"))
@dp.callback_query(CheckAvailability.you_sure, F.data == "back")
@dp.callback_query(CheckAvailability.not_correct_number, F.data == "back")
async def check_availability_add_to_cart(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    if callback.data != "back":
        item_id = callback.data.split('|')[1]
        stocks = callback.data.split('|')[2]
        cena = callback.data.split('|')[3]

        await state.update_data(item_id=item_id)
        await state.update_data(item_name=get_item_name_by_id(item_id))
        await state.update_data(stocks=stocks)
        await state.update_data(cena=cena)
    else:
        data = await state.get_data()
        stocks = data['stocks']

    await callback.message.answer(text=f"Введите количество не более {stocks} шт.", reply_markup=kb.as_markup())
    await state.set_state(CheckAvailability.add_to_cart)


@dp.message(CheckAvailability.add_to_cart)
async def check_availability_choose_quantity(message: Message, state: FSMContext):
    data = await state.get_data()
    cena = data['cena']
    quantity = message.text
    await state.update_data(quantity=quantity)
    kb = create_kb()
    if message.text.isdigit() and 0 < int(message.text) <= int(data['stocks']):
        summa = int(cena) * int(quantity)
        await state.update_data(summa=summa)

        kb.add(
            InlineKeyboardButton(text="Добавить в корзину", callback_data="complete adding to cart")
        )
        kb.adjust(1)
        await message.answer(
            text=f"Товар <b>{data['item_name']}</b>\nв количестве <b>{quantity}</b> шт.\nбудет стоить <b>{summa}</b> рублей",
            reply_markup=kb.as_markup()
        )
        await state.set_state(CheckAvailability.you_sure)
    else:
        await message.answer(text="Введите корректное число", reply_markup=kb.as_markup())
        await state.set_state(CheckAvailability.not_correct_number)


@dp.callback_query(CheckAvailability.you_sure)
async def check_availability_choose_quantity(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text="Продолжить поиск", callback_data="resume searching"),
        InlineKeyboardButton(text="В корзину", callback_data="cart"),
    )
    kb.adjust(1)

    data['user_cart'].append(
        {'item_id': data['item_id'],
         'item_name': data['item_name'],
         'item_quantity': data['quantity'],
         'summa': data['summa']
         })
    updated_cart = data['user_cart']
    await state.update_data(user_cart=updated_cart)
    data_2 = await state.get_data()
    print(data_2['user_cart'])
    await callback.message.answer(
        text=f"Товар <b>{data['item_name']}</b> добавлен в корзину в количестве <b>{data['quantity']}</b> шт.",
        reply_markup=kb.as_markup())
    await state.set_state(CheckAvailability.choose_quantity)


@dp.callback_query(F.data == "cart")
@dp.callback_query(Cart.input_city, F.data == "back")
async def cart_start(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    base_str = 'Ваша корзина:'
    data = await state.get_data()
    user_cart = data['user_cart']
    total = 0

    # # ТЕСТОВАЯ ТЕМА!!!
    # data['user_cart'].append(
    #     {'item_id': "00-01016729",
    #      'item_name': 'Патронный нагреватель 6 мм, 220 В (6 х 40 мм, 80 Вт)',
    #      'item_quantity': "3",
    #      'summa': "3000"
    #      })
    # updated_cart = data['user_cart']
    # await state.update_data(user_cart=updated_cart)
    # # ТЕСТОВАЯ ТЕМА!!!

    if not data['user_auth']:
        auth_button = InlineKeyboardButton(text="Авторизоваться", callback_data="auth")
        kb.add(auth_button)
        kb.adjust(1)
        base_str += "\n Чтобы оформить заказ необходима авторизация"
    else:
        for item in user_cart:
            total += int(item['summa'])
            base_str += f'\n<b>{item["item_name"]}</b> - <b>{item["item_quantity"]} шт</b> за <b>{item["summa"]} рублей</b>'
        base_str += f"\n\nВсего <b>{total}</b> рублей"
        if total != 0:
            kb.add(InlineKeyboardButton(text="Оформить заказ", callback_data="checkout"))
            kb.adjust(1)
        await state.update_data(total=total)
    await callback.message.answer(text=base_str, reply_markup=kb.as_markup())
    await state.set_state(Cart.start)


@dp.callback_query(Cart.start, F.data == "checkout")
@dp.callback_query(Cart.input_street, F.data == "back")
async def cart_checkout_start(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text="Введите город доставки", reply_markup=kb.as_markup())
    await state.set_state(Cart.input_city)


@dp.message(Cart.input_city)
async def cart_checkout_input_street(message: Message, state: FSMContext):
    kb = create_kb()
    city = message.text
    await state.update_data(city=city)
    await message.answer(text=f"Город: <b>{city}\n</b>Введите улицу доставки", reply_markup=kb.as_markup())
    await state.set_state(Cart.input_street)


@dp.callback_query(Cart.input_house)
async def cart_checkout_back_to_input_street(callback: Message, state: FSMContext):
    kb = create_kb()
    data = await state.get_data()
    city = data['city']
    await callback.message.answer(text=f"Город: <b>{city}\n</b>Введите улицу доставки", reply_markup=kb.as_markup())
    await state.set_state(Cart.input_street)


@dp.message(Cart.input_street)
async def cart_checkout_input_house(message: Message, state: FSMContext):
    data = await state.get_data()
    city = data['city']
    kb = create_kb()
    street = message.text
    await state.update_data(street=street)
    await message.answer(text=f"Город: <b>{city}</b>\nУлица: <b>{street}</b>\nВведите дом доставки", reply_markup=kb.as_markup())
    await state.set_state(Cart.input_house)


@dp.callback_query(Cart.final, F.data == "back")
async def cart_checkout_back_to_input_house(callback: Message, state: FSMContext):
    kb = create_kb()
    data = await state.get_data()
    city = data['city']
    street = data['street']
    await callback.message.answer(text=f"Город: <b>{city}</b>\nУлица: <b>{street}</b>\nВведите дом доставки", reply_markup=kb.as_markup())
    await state.set_state(Cart.input_house)


@dp.message(Cart.input_house)
async def cart_checkout_final(message: Message, state: FSMContext):
    data = await state.get_data()
    city = data['city']
    street = data['street']
    house = message.text
    kb = create_kb()
    kb.add(InlineKeyboardButton(text="Оплатить заказ", callback_data="pay"))
    await state.update_data(house=house)
    await message.answer(text=f"Город: <b>{city}</b>\nУлица: <b>{street}</b>\nДом: <b>{house}</b>\nВсе ли верно?", reply_markup=kb.as_markup())
    await state.set_state(Cart.final)


@dp.callback_query(Cart.final, F.data == "pay")
async def cart_checkout_pay(callback: CallbackQuery, state: FSMContext):
    kb = create_kb("На главную")
    data = await state.get_data()
    result_zakaz = ""
    user_cart = data['user_cart']
    for item in user_cart:
        result_zakaz += str(item["item_id"]) + ':'
        result_zakaz += str(item["item_quantity"]) + ';'
        result_zakaz += str(item["summa"]) + '^'
    current_date = datetime.datetime.now().strftime('%d-%m-%Y')
    current_time = datetime.datetime.now().time()
    dost = "Курьер"
    city = data['city']
    street = data['street']
    house = data['house']
    email = data['email']
    id_user = callback.from_user.id
    create_order_db(result_zakaz, current_date, current_time, dost, city, street, house, email, id_user)
    print(result_zakaz, current_date, current_time)
    await callback.message.answer(text="Заказ успешно оформлен", reply_markup=kb.as_markup())
    await state.set_state(Cart.pay)


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
    await callback.message.answer_photo(photo='https://imgur.com/a/LRsILZY', caption=pvz_text,
                                        reply_markup=kb.as_markup())
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
    await callback.message.answer(text=beskontaktnaya_kurierskaya_text, reply_markup=kb.as_markup(),
                                  parse_mode=ParseMode.HTML)
    await state.set_state(DeliveryMethods.method)


@dp.callback_query(DeliveryMethods.delivery_methods, F.data == "4")
async def punkti_samovivoza(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=punkti_samovivoza_text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
    await state.set_state(DeliveryMethods.method)


@dp.callback_query(DeliveryMethods.delivery_methods, F.data == "5")
async def kurierskaya_po_vsei_rossii(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=kurierskaya_po_vsei_rossii_text, reply_markup=kb.as_markup(),
                                  parse_mode=ParseMode.HTML)
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
    await callback.message.answer(text=transfer_to_bank_card_text, reply_markup=kb.as_markup(),
                                  parse_mode=ParseMode.HTML, )
    await state.set_state(PaymentMethods.method)


@dp.callback_query(PaymentMethods.payment_methods, F.data == "3")
async def transfer_to_e_wallet_card(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=transfer_to_e_wallet_text, reply_markup=kb.as_markup(),
                                  parse_mode=ParseMode.HTML, )
    await state.set_state(PaymentMethods.method)


@dp.callback_query(PaymentMethods.payment_methods, F.data == "4")
async def money_transfer_systems(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=money_transfer_systems_text, reply_markup=kb.as_markup(),
                                  parse_mode=ParseMode.HTML, )
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
        InlineKeyboardButton(text="Как найти товар", callback_data="how to search"),
        InlineKeyboardButton(text="Какая стоимость журнала", callback_data="price of magazine"),
        InlineKeyboardButton(text="Способы оплаты", callback_data="payment methods"),
        InlineKeyboardButton(text="График работы / Адрес", callback_data="grafik raboty"),
        InlineKeyboardButton(text="Как добраться", callback_data="how to get"),
        InlineKeyboardButton(text="Способы доставки", callback_data="delivery methods"),
    )
    kb.adjust(1)
    await callback.message.answer(text="Введите свой вопрос или выберите из списка", reply_markup=kb.as_markup())
    await state.set_state(AskQuestion.start)


@dp.message(AskQuestion.start)
async def ask_openai(message: Message, state: FSMContext):
    print("yoo")
    kb = create_kb()
    kb.add(InlineKeyboardButton(text="Вызвать менеджера", callback_data="call manager"))
    kb.adjust(1)
    question = message.text
    response = await get_openai_response(question)
    await message.answer(text=response, reply_markup=kb.as_markup())


@dp.callback_query(F.data == "call manager")
async def ask_question_call_manager(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Напишите вопрос менеджеру")
    await state.set_state(AskQuestion.call_manager)


@dp.message(AskQuestion.call_manager)
async def ask_openai(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(text="Направил этот вопрос менеджеру, пожалуйста, ожидайте")
    text = f"Новый вопрос от пользователя {message.from_user.username}\nПочта {data['email']}\nВопрос: {message.text}"
    await bot.send_message(chat_id=816831722, text=text)

@dp.callback_query(F.data == "how to order")
async def how_to_order_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="В разработке")
    # TODO


@dp.callback_query(F.data == "how to choose magazine")
async def how_to_choose_magazine(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="В разработке")
    # TODO


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
