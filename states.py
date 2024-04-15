from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class StartState(StatesGroup):
    start_state = State()


class CreateAccount(StatesGroup):
    get_name_and_surname = State()
    get_email = State()
    get_phone = State()
    get_password = State()
    get_password_again = State()


class Login(StatesGroup):
    input_login = State()
    input_password = State()


class MakeOrder(StatesGroup):
    choose_product = State()
    choose_quantity = State()
    create_order = State()


class Logout(StatesGroup):
    confirm_logout = State()


class TrackOrder(StatesGroup):
    choose_order = State()
    track_order = State()


class CheckStatus(StatesGroup):
    start = State()
    choose_order = State()
    input_fio = State()
    input_email = State()
    input_password = State()
    repeat_password = State()
    input_order_number = State()


class Auth(StatesGroup):
    input_email = State()
    input_password = State()


class CheckAvailability(StatesGroup):
    start = State()
    add_to_cart = State()
    choose_quantity = State()
    pzc = State()
    you_sure = State()
    not_correct_number = State()


class HowToSearch(StatesGroup):
    how_to_search = State()


class HowToGet(StatesGroup):
    how_to_get = State()


class DeliveryMethods(StatesGroup):
    delivery_methods = State()
    method = State()


class PaymentMethods(StatesGroup):
    payment_methods = State()
    method = State()


class Cart(StatesGroup):
    start = State()
    input_city = State()
    input_street = State()
    input_house = State()
    final = State()
    pay = State()



class Misc(StatesGroup):
    misc = State()


class AskQuestion(StatesGroup):
    start = State()
