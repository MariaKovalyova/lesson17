from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy

from schemas import movie_schema, movies_schema  # Импорт схем из файла schemas.py
from models import *  # Импорт классов для работы с БД

"""Конфигурация приложения"""
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Адрес базы данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTX-JSON'] = {'ensure_ascii': False, 'indent': 3}

db = SQLAlchemy(app)

api = Api(app)  # Подключение Api
movie_ns = api.namespace('movies')


@movie_ns.route("/")  # Основная страница
class MovieView(Resource):

    def get(self):
        all_movies = db.session.query(Movie.id,
                                        Movie.title,
                                        Movie.description,
                                        Movie.rating,
                                        Movie.trailer,
                                        Genre.name.label('genre'),
                                        Director.name.label('director')).join(Genre).join(Director)

        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            all_movies = all_movies.filter(Movie.director_id == director_id)
        if genre_id:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(all_movies), 200

    def post(self):  # Добавление нового элемента в базу данных
        req_json = request.json
        new_moive = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_moive)
        return f"Новый фильм {new_moive.id} добавлен", 201


@movie_ns.route("/<int:movie_id>")  # Действие с объектом БД по его id
class MovieView(Resource):

    def get(self, movie_id: int):  # Получение объекта по ид
        movie = db.session.query(Movie).get(movie_id)
        if movie:
            return movie_schema.dump(movie), 200
        return "Фильм не найден", 404

    def put(self, movie_id: int):  # Обновление объекта по ИД
        movie = db.session.query(Movie).get(movie_id)  # Запрос из БД нужного объекта по ИД
        if not movie:  # Если объекта с нужным ИД не найдено, то возврат ошибки
            return f"Такого фильма c ид {movie_id} нет", 404
        req_json = request.json

        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.trailer = req_json['trailer']
        movie.year = req_json['year']
        movie.rating = req_json['rating']
        movie.genre_id = req_json['genre_id']
        movie.director_id = req_json['director_id']

        db.session.add(movie)
        db.session.commit()
        return f"Фильм c ид {movie_id} обновлён", 204

    def delete(self, movie_id: int):  # Удаление объекта по ид
        movie_to_del = db.session.query(Movie).get(movie_id)
        if not movie_to_del:
            return f"Фильм с ид {movie_id} не найден", 404
        db.session.delete(movie_to_del)
        db.session.commit()
        return 201


if __name__ == '__main__':
    app.run(debug=True)
