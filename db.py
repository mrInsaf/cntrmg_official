import sqlite3
from datetime import datetime

conn = sqlite3.connect('База данных/centrmag.db')  # Замените 'mydatabase.db' на имя вашей базы данных
cursor = conn.cursor()

def select(query):
    query = query
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.commit()
    return rows

def insert(table_name, data_list, auto_increment_id):
    # Получаем информацию о столбцах в таблице
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    columns = columns[auto_increment_id:]
    print(columns)

    # Генерируем SQL-запрос для вставки данных
    placeholders = ', '.join(['?'] * len(columns))
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    # Вставляем данные в таблицу
    cursor.execute(query, data_list)
    conn.commit()

    # Закрываем соединение с базой данных
    conn.close()


def register_user(data_list, chat_id):
    query = 'insert into users(chat_id, name, surname, email, phone, password) values (?, ?, ?, ?, ?, ?)'
    # Вставляем данные в таблицу
    cursor.execute(query, data_list)
    conn.commit()


def get_login_and_password_by_id(chat_id):
    rows = select(f'select email, password from users where chat_id = "{chat_id}"')
    return rows[0]


def get_password_by_email(email):
    rows = select(f'select password from users where email = "{email}"')
    return rows[0][0]


def check_login_in_db(login):
    rows = select(f'select * from users where email = "{login}"')
    if not rows:
        return False
    else:
        return True


def set_authorised(chat_id):
    select(f'UPDATE users SET authorised = 1 WHERE chat_id = "{chat_id}"')



def set_unauthorised(chat_id):
    select(f'UPDATE users SET authorised = 0 WHERE chat_id = "{chat_id}"')


def check_chat_id_in_db(chat_id):
    rows = select(f'select * from users where chat_id = {chat_id}')
    if not rows:
        return False
    else:
        return True


def check_authorisation(chat_id):
    if select(f'select authorised from users where chat_id = {chat_id}')[0][0] == 1:
        return True
    else:
        return False

def get_products():
    return select(f'select product_id, name, quantity, price, c.category_name from products p join categories c on '
                  f'p.category = c.category_id')


def get_info_about_product(product_id):
    return select(f'select product_id, name, quantity, price, c.category_name from products p join categories c on '
                  f'p.category = c.category_id where product_id = {product_id}')[0]


def get_product_name_by_id(product_id):
    return select(f'select name from products where product_id = {product_id}')[0][0]


def create_order_in_db(chat_id, status="new"):
    dttm = datetime.now()
    query = f'insert into orders(datetime, user_id, status) values ("{dttm}", {chat_id}, "{status}")'

    # Вставляем данные в таблицу
    cursor.execute(query)
    conn.commit()

    last_chat_id = cursor.lastrowid
    return last_chat_id


def push_order_sum(order_id, summa):
    select(f'UPDATE orders SET summa = {summa} WHERE order_id = "{order_id}"')


def get_product_price_by_id(product_id):
    return select(f"select price from products where product_id = {product_id}")[0][0]


def insert_order_item(order_id, product_id, quantity, summa):
    query = f'insert into order_items (order_id, product_id, quantity, summa) values ({order_id}, {product_id}, {quantity}, {summa})'

    # Вставляем данные в таблицу
    cursor.execute(query)
    conn.commit()


def set_order_status(order_id, status):
    select(f'UPDATE orders SET status = "{status}" WHERE order_id = {order_id}')


def get_orders_by_chat_id(chat_id):
    return select(f"select * from orders where user_id = {chat_id} and status != \"new\" ")


def get_info_about_order(order_id):
    return select(f'select * from orders where order_id = {order_id}')[0]


def get_items_by_order_id(order_id):
    return select(f'select name, oi.quantity, summa from order_items oi join products p on oi.product_id = p.product_id where order_id = {order_id}')

