import mysql.connector
from mysql_config import *

cnx = mysql.connector.connect(user=username, password=password,
                              host=host,
                              database=database)
cursor = cnx.cursor()


def get_res_by_item_name(item_name):
    cursor.execute(
        f"SELECT ost, nal, proizvodim, cena_str, Id, obl, cena, ogl FROM main WHERE ogl LIKE '%{item_name}%'"
    )
    rows = cursor.fetchall()
    result = []
    for row in rows:
        row_dict = {
            'ost': row[0],
            'nal': row[1],
            'proizvodim': row[2],
            'cena_str': row[3],
            'Id': row[4],
            'obl': row[5],
            'cena': row[6],
            'ogl': row[7],
        }
        result.append(row_dict)
    if len(result) != 0:
        return result[0]
    else:
        return None


def get_stocks(item_name):
    res = get_res_by_item_name(item_name)
    if res is not None:
        print(res)
        stocks = 0
        if res['ost'] > 0:
            stocks = res['ost']
        if res['nal'] > 0:
            stocks = 1000
        if res['proizvodim'] > 0:
            stocks = 1000
        if res['cena_str'] > 0:
            stocks = 1000
        return res, stocks
    else:
        return None, None


def get_item_name_by_id(item_id):
    cursor.execute(
        f'select ogl from main where Id = "{item_id}"'
    )
    rows = cursor.fetchall()
    return rows[0][0]


def get_zakaz_by_id(zakaz_id):
    cursor.execute(
        f'select * from zakazy '
        f'where Id = {zakaz_id}'
    )
    rows = cursor.fetchall()
    if rows is not None:
        zakaz = rows[0]
        result_dict = {
            'zakaz': zakaz[2],
            'data': zakaz[4],
            'time': zakaz[5],
            'dost': zakaz[6],

        }
    return rows[0]


def register_user(user_id, username, password, fio, email):
    try:
        cursor.execute(
            f"INSERT INTO users (id_user, nik, pass, fam, email, prava) "
            f"VALUES ('{user_id}', '{username}', '{password}', '{fio}', '{email}', 'user')"
        )
        cnx.commit()
        print("User added successfully.")
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False


def check_user_in_db(email):
    cursor.execute(
        f'select * from users where email = "{email}"'
    )
    rows = cursor.fetchall()
    if len(rows) > 0 and len(rows[0]) > 0:
        return True
    else:
        return False


def check_password(email, password):
    cursor.execute(
        f'select pass from users where email = "{email}"'
    )
    rows = cursor.fetchall()
    if len(rows) > 0 and len(rows[0]) > 0 and password == rows[0][0]:
        return True
    else:
        return False



def create_order_db(zakaz, date, time, dost, city, street, house, email, id_user):
    try:
        cursor.execute(
            f"INSERT INTO zakazy (zakaz, data, time, dost, city, street, home, email, id_user) "
            f"VALUES ('{zakaz}', '{date}', '{time}', '{dost}', '{city}', '{street}', '{house}', '{email}', '{id_user}')"
        )
        cnx.commit()
        print("заказ добавлен")
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False


def select_orders_by_email(email):
    cursor.execute(
        f'select zakaz, data, time, Id, city, street, home from zakazy where email = "{email}"'
    )
    rows = cursor.fetchall()
    order_items = []
    for i, order in enumerate(rows):
        zakaz = order[0]
        items = zakaz.split('^')
        order_items.append({'order_id': order[3], "zakaz": [], "data": "", "time": ""})
        for item in items:
            if len(item) == 0:
                break
            item_info = item.split(':')
            item_id = item_info[0]
            item_name = select_item_by_id(item_id)
            quantity = item_info[1].split(';')[0]
            summa = item_info[1].split(';')[1]
            item_dict = {'item_id': item_id, 'item_name': item_name, 'quantity': quantity, 'summa': summa}
            order_items[i]['zakaz'].append(item_dict)
        order_items[i]['data'] = order[1]
        order_items[i]['time'] = order[2]
        order_items[i]['city'] = order[4]
        order_items[i]['street'] = order[5]
        order_items[i]['home'] = order[6]
    return order_items


def select_item_by_id(item_id):
    cursor.execute(
        f'select ogl from main where Id = "{item_id}"'
    )
    rows = cursor.fetchall()
    return rows[0][0]

#
print(select_orders_by_email('mr.insaf@list.ru'))