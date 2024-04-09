import mysql.connector
from mysql_config import *

cnx = mysql.connector.connect(user=username, password=password,
                              host=host,
                              database=database)
cursor = cnx.cursor()


def get_res_by_item_name(item_name):
    cursor.execute(
        "SELECT ost, nal, proizvodim, cena_str, Id, obl, cena FROM main WHERE ogl = %s",
        (item_name,)
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
