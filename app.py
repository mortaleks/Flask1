from typing import Any
from flask import Flask, jsonify, request
from random import choice
    
app = Flask(__name__)
app.json.ensure_ascii = False


about_me = {
    "name": "Алексей",
    "surname": "Куксов",
    "email": "aleksey.kuksov@gmail.com"
 }

quotes = [
    {
        "id": 1,
        "author": "Rick Cook",
        "text": "Программирование сегодня — это гонка \
разработчиков программ, стремящихся писать программы с \
большей и лучшей идиотоустойчивостью, и вселенной, которая \
пытается создать больше отборных идиотов. Пока вселенная \
побеждает.",
    },
    {
        "id": 2,
        "author": "Waldi Ravens",
        "text": "Программирование на С похоже на быстрые танцы \
на только что отполированном полу людей с острыми бритвами в \
руках.",
    },
    {
        "id": 3,
        "author": "Mosher’s Law of Software Engineering",
        "text": "Не волнуйтесь, если что-то не работает. Если \
бы всё работало, вас бы уволили.",
    },
    {
        "id": 4,
        "author": "Yoggi Berra",
        "text": "В теории, теория и практика неразделимы. На \
практике это не так.",
    },
]


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/about")
def about():
    return jsonify(about_me), 200

# 1,2
@app.route("/quotes")
def get_quotes() -> list[dict[str, Any]]:
    """Функция неявно преобразовывает список словарей в JSON"""
    return quotes

@app.route("/quotes/<int:quote_id>")
def quote(quote_id=None):
    if quote_id:
        for quote in quotes:
            if quote["id"] == quote_id:
                return quote
        return f"Quote with id={quote_id} not found", 404


# 3
@app.route("/count")
def count():
    return {"count": len(quotes)}


# 4
@app.route("/quotes/random")
def rand():
    return quotes[choice(range(len(quotes)))]


@app.route("/params/<value>")
def param_example(value: Any):
    return jsonify(param=value)

@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    last_quote = quotes[-1]
    new_id = last_quote["id"] + 1
    new_quote["id"] = new_id
    quotes.append(new_quote)
    #print("data = ", data)
    return jsonify(new_quote), 201

@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id: int):
    for quote in quotes:
        if quote["id"] == quote_id:
            quotes.remove(quote)
            return jsonify({"message": f"Quote with id={quote_id} has deleted"}), 200
    return f"Quote with id={quote_id} not found", 404

@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    new_data = request.json
    for quote in quotes:
        if quote["id"] == quote_id:
            quote.update(new_data)
            return jsonify({"message": f"Quote with id={quote_id} has updated"}), 200
    return f"Quote with id={quote_id} not found", 404

if __name__ == "__main__":
    app.run(debug=True)