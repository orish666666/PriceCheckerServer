import sqlite3


def get_categories():
    connection = sqlite3.connect(f"products.sqlite")
    sql_query = f""" SELECT DISTINCT category_id, category_name FROM predictions """
    res = connection.execute(sql_query).fetchall()
    connection.commit()
    connection.close()
    return res


def get_prediction_graph_by_id(category_id, freq):
    connection = sqlite3.connect(f"products.sqlite")
    sql_query = f""" SELECT DISTINCT image_graph, category_name FROM predictions
                     WHERE category_id = {category_id} AND frequency = '{freq}'"""
    res = connection.execute(sql_query).fetchone()
    connection.commit()
    connection.close()
    return res


def insert_products(data_to_insert):
    connection = sqlite3.connect(f"products.sqlite")
    sql_insert = """ INSERT OR REPLACE INTO products (id, category_id, name, price, date, category_name)
                     VALUES (?,?,?,?,?,?) """
    connection.executemany(sql_insert, data_to_insert)
    connection.commit()
    connection.close()


def get_products():
    connection = sqlite3.connect(f"products.sqlite")
    sql_query = """ SELECT category_id, category_name, price, date FROM products """
    res = connection.execute(sql_query).fetchall()
    connection.commit()
    connection.close()
    return res


def insert_predictions(data_to_insert):
    connection = sqlite3.connect(f"products.sqlite")
    sql_insert = """ INSERT OR IGNORE INTO predictions (category_id, category_name, frequency, image_graph)
                     VALUES (?,?,?,?) """
    connection.executemany(sql_insert, data_to_insert)
    connection.commit()
    connection.close()


def delete_predictions():
    connection = sqlite3.connect(f"products.sqlite")
    sql_delete = """ DELETE FROM predictions """
    connection.execute(sql_delete)
    connection.commit()
    connection.close()
