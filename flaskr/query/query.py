import sqlite3


def insert_products(data_to_insert):
    print(data_to_insert)
    connection = sqlite3.connect(f"products.sqlite")
    sql_insert = """ INSERT OR REPLACE INTO products (id, category_id, name, price, date, category_name)
                     VALUES (?,?,?,?,?,?) """
    connection.executemany(sql_insert, data_to_insert)
    connection.commit()
    connection.close()
