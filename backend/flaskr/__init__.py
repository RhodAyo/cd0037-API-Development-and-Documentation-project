# NAME: OLUWOLE AYOMIDE RHODA

import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql.functions import random
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_question(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Setting up CORS to allow '*' for origins.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # using after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # Endpoint to handle GET requests for all available categories.
    @app.route("/categories")
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        categories_type = Category.query.order_by(Category.type).all()
        formatted_cat = [category.format() for category in categories]
        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": {
                    category.id: category.type for category in categories
                },
                "total_categories": len(Category.query.all()),
            }
        )

    # Endpoint to GET requests for questions incuding pagination of 10 questions, number of total questions,current category,categories

    @app.route('/questions')
    def get_questions():
        # selection instance retrieves the questions in thq Question db by ID
        selection = Question.query.order_by(Question.id).all()
        # cureent_question handles the pagination based on the id of Questions.
        current_question = paginate_question(request, selection)
        categories_type = Category.query.order_by(Category.type).all()

        if len(current_question) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_question,
                "total_questions": len(Question.query.all()),
                "categories": {category.id: category.type for category in categories_type},
                "current_category": None
            }
        )

    # Endpoint to DELETE questions using the question ID
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_question(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_question,
                    "total_question": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    # Endpoint to handle POST for new questions that requires question and answer text, category and difficulty score.
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_difficulty = body.get("difficulty", None)
        new_category = body.get("category", None)

        try:
            questions = Question(question=new_question, answer=new_answer,
                                 difficulty=new_difficulty, category=new_category)
            questions.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_question(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": questions.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    # Endpoint to get questions based on a search term , result returns questions for whom the search term is a substring of the question.
    @app.route("/questions/search", methods=["POST"])
    def question_search():
        search_word = request.get_json().get('searchTerm')

        if search_word:
            # This gets questions related to the substring
            search_result = Question.query.filter(
                Question.question.ilike(f'%{search_word}%')).all()

            return jsonify({
                "success": True,
                "questions": [search.format() for search in search_result],
                "total_questions": len(search_result),
                "current_category": None
            })
        abort(404)

    # A GET endpoint to obtain questions based on category
    @app.route("/categories/<int:category_id>/questions")
    def get_questions_categories(category_id):

        cat_question = Question.query.filter(
            Question.category == category_id).all()

        if len(cat_question) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": [question.format() for question in cat_question],
                "total_question": len(cat_question),
                "current_category": category_id
            }
        )


# A POST endpoint to get questions to play the quiz.This endpoint should take category and previous question parameters and return a random questions within the given category,  if provided,and that is not one of the previous questions.

    @app.route("/quizzes", methods=['POST'])
    def get_quiz():
        try:
            if not request.get_json():
                abort(422)

            previous_questions = request.get_json().get('previous_questions')
            quiz_category = request.get_json().get('quiz_category')

            # If the quiz category is selected id 'ALL' :
            if quiz_category:
                # When category match the category from the request, questions not in previous_questionsand not asked already are retrieved
                extra_question = Question.query.filter_by(category=quiz_category).filter(
                    Question.id.notin_(previous_questions)).order_by(random()).all()
            else:
                extra_question = Question.query.filter(
                    Question.id.notin_(previous_questions)).order_by(random()).all()

            total_questions = len(extra_question)
            if total_questions > 0:
                for question in extra_question:
                    current_question = question.format()
            else:
                current_question = None

            return jsonify({
                "success": True,
                "question": current_question
            })

        except:
            abort(422)

    # These different errors in the 4xx and 5xx categories, using error handlers to handle them
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404,
                    "message": "Resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422,
                    "message": "Unprocessable: Server could not process your request"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad request: Check requests again"}), 400

    @app.errorhandler(500)
    def server_error(error):
        return (
            jsonify({"success": False, "error": 500,
                     "message": "Internal Server Error"}),
            500,
        )
    return app
