from typing import Any
from random import choice
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, abort, request
from pathlib import Path
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from flask_migrate import Migrate
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Base(DeclarativeBase):
    pass

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "store.db" # <- тут путь к БД

app = Flask(__name__)
app.json.ensure_ascii = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)

class AuthorModel(db.Model):
    __tablename__ = 'authors'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(32), index= True, unique=True)
    quotes: Mapped[list['QuoteModel']] = relationship( back_populates='author', lazy='dynamic')
    
    def __init__(self, name):
        self.name = name
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
            }

class QuoteModel(db.Model):
    __tablename__ = 'quotes'
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey('authors.id'))
    author: Mapped['AuthorModel'] = relationship(back_populates='quotes')
    text: Mapped[str] = mapped_column(String(255))

    def __init__(self, author, text):
        self.author = author
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text
        }

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
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    quotes = []
    for quote in quotes_db:
        quotes.append(quote.to_dict())
    return jsonify(quotes), 200

@app.route("/authors/<int:author_id>/quotes")
def get_author_quotes(author_id):
    """Функция неявно преобразовывает список словарей в JSON"""
    author  = db.session.get(AuthorModel, author_id)
    quotes = []
    for quote in author.quotes:
        quotes.append(quote.to_dict())
    return jsonify(author = author.to_dict(), quotes = quotes), 200


@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id: int):
    select_quote = db.get_or_404(QuoteModel, quote_id, description=f"Quote with id={quote_id} not found")
    quote = select_quote.to_dict()
    return jsonify(quote), 200


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
    quote = QuoteModel(**new_quote)
    db.session.add(quote)
    db.session.commit()
    return jsonify(quote.to_dict()), 201

@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id: int):
    select_quote = db.get_or_404(QuoteModel, quote_id, description=f"Quote with id={quote_id} not found")
    db.session.delete(select_quote)
    db.session.commit()
    return jsonify({"message": f"Quote with id={quote_id} has deleted"}), 200

@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    select_quote = db.get_or_404(QuoteModel, quote_id, description=f"Quote with id={quote_id} not found")
    new_data = request.json
    for key, value in new_data.items():
        setattr(select_quote, key, value)
    db.session.commit()    
    return jsonify({"message": f"Quote with id={quote_id} has updated"}), 200

if __name__ == "__main__":
    app.run(debug=True)