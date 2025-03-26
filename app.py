from typing import Any
from flask import Flask, jsonify, request
from random import choice
from pathlib import Path
import sqlite3



BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "store.db" # <- тут путь к БД

app = Flask(__name__)
app.json.ensure_ascii = False


# quotes = [
#     {
#         "id": 1,
#         "author": "Rick Cook",
#         "text": "Программирование сегодня — это гонка \
# разработчиков программ, стремящихся писать программы с \
# большей и лучшей идиотоустойчивостью, и вселенной, которая \
# пытается создать больше отборных идиотов. Пока вселенная \
# побеждает.",
#     },
#     {
#         "id": 2,
#         "author": "Waldi Ravens",
#         "text": "Программирование на С похоже на быстрые танцы \
# на только что отполированном полу людей с острыми бритвами в \
# руках.",
#     },
#     {
#         "id": 3,
#         "author": "Mosher’s Law of Software Engineering",
#         "text": "Не волнуйтесь, если что-то не работает. Если \
# бы всё работало, вас бы уволили.",
#     },
#     {
#         "id": 4,
#         "author": "Yoggi Berra",
#         "text": "В теории, теория и практика неразделимы. На \
# практике это не так.",
#     },
# ]


# 1,2
@app.route("/quotes")
def get_quotes() -> list[dict[str, Any]]:
    """Функция неявно преобразовывает список словарей в JSON"""
    select_quotes = "SELECT * from quotes"
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    cursor.execute(select_quotes)
    quotes_db = cursor.fetchall()
    cursor.close()
    connection.close()
    
    keys = ("id", "author", "text")
    quotes= []
    for quote_db in quotes_db:
        quote = dict(zip(keys, quote_db))
        quotes.append(quote)
    return jsonify(quotes), 200
    

    return quotes


@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
    select_quote = "SELECT * FROM quotes WHERE id = ?"
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    quote_db = cursor.execute(select_quote, (quote_id,)).fetchone()
    cursor.close()
    connection.close()
    if quote_db:
        keys = ("id", "author", "text")
        quote = dict(zip(keys, quote_db))
        return jsonify(quote), 200
    return f"Quote with id={quote_id} not found", 404


# 3
# @app.route("/count")
# def count():
#     return {"count": len(quotes)}


# 4
# @app.route("/quotes/random")
# def rand():
#     return quotes[choice(range(len(quotes)))]


# @app.route("/params/<value>")
# def param_example(value: Any):
#     return jsonify(param=value)

@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    insert_quote = "INSERT INTO quotes (author, text) VALUES (?, ?)"
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    cursor.execute(insert_quote, (new_quote['author'], new_quote['text']))
    new_quote_db = cursor.lastrowid
    connection.commit()
    cursor.close()
    connection.close()
    new_quote['id'] = new_quote_db
    return jsonify(new_quote), 201

@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id: int):
    delete_sql = f"DELETE FROM quotes WHERE id = ?"
    params = (quote_id,)
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    cursor.execute(delete_sql, params)
    connection.commit()
    rows = cursor.rowcount
    cursor.close()
    connection.close()
    if rows:
        return jsonify(f"Quote with {id=} is deleted."), 200
    return f"Quote with id={quote_id} not found", 404

@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    new_data = request.json
    attributes: set = set(new_data.keys()) & {'author', 'text'}
    update_quote = f"UPDATE quotes SET {', '.join(attr + '=?' for attr in attributes)} WHERE id = ?"
    params = tuple(new_data.get(attr) for attr in attributes) + (quote_id,)
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    cursor.execute(update_quote, params)
    connection.commit()
    rows = cursor.rowcount
    cursor.close()
    connection.close()
    if rows:
        return jsonify({"message": f"Quote with id={quote_id} has updated"}), 200
    return f"Quote with id={quote_id} not found", 404

if __name__ == "__main__":
    app.run(debug=True)