import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8


def paginate_books(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    current_books = [book.format()for book in selection]

    return current_books[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/books')
    def get_books():
        books = Book.query.order_by(Book.id).all()
        current_books = paginate_books(request, books)
        if len(current_books) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'books': current_books,
            'total_books': len(books)
        })

    @app.route('/books/<book_id>', methods=['PATCH'])
    def update_rating(book_id):
        body = request.get_json()

        if body is None:
            abort(422)

        book = Book.query.get(book_id)

        if book is None:
            abort(404)

        try:
            book.rating = body.get('rating')
            book.update()

            return jsonify({
                'success': True,
                'book': book.format()
            })
        except Exception as e:
            print(e)
            abort(422)

    @app.route('/books/<book_id>', methods=['DELETE'])
    def delete_book(book_id):
        book = Book.query.get(book_id)

        if book is None:
            abort(404)

        book.delete()
        books = Book.query.order_by(Book.id).all()
        return jsonify({
            'success': True,
            'deleted_id': book_id,
            'books': [book.format() for book in books],
            'total_books': len(books)
        })

    @app.route('/books', methods=['POST'])
    def create_book():
        body = request.get_json()

        if body is None:
            abort(422)

        title = body.get('title')
        author = body.get('author')
        rating = body.get('rating')

        if title and author and rating:
            book = Book(title, author, rating)
            book.insert()
            books = Book.query.order_by(Book.id).all()

            return jsonify({
                'success': True,
                'deleted_id': book.id,
                'books': [book.format() for book in books],
                'total_books': len(books)
            })

    return app
