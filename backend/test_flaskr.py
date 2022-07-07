import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres", "rhodayo10.", "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "A test question?",
                             "answer": "Test Answer",
                             "difficulty": 2,
                             "category": 3}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_error_paginated_questions(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    def test_persist_delete_question(self):
        test_case = Question(
            question='test question', answer='test answer', difficulty=1, category=2)
        test_case.insert()

        res = self.client().delete('/questions/{}'.format(test_case.id))
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == test_case.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], test_case.id)
        self.assertEqual(question, None)

    def test_error_persist_delete_question(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(
            data["message"], "Unprocessable: Server could not process your request")

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        pass

    def test_error_new_question_fails(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        pass

    def test_get_question_search_with_results(self):
        search = {'searchTerm': 'title'}
        res = self.client().post("/questions/search", json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_error_question_search_with_results(self):
        empty_search = {'searchTerm': ''}
        res = self.client().post("/questions/search", json=empty_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    def test_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_question"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["current_category"])

    def test_error_category_questions(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    def test_quiz_questions(self):
        test_quiz = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Entertainment',
                'id': 3
            }
        }

        res = self.client().post('/quizzes', json=test_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_error_quiz_questions(self):
        test_quiz = {
            'quiz_category': {
                'type': 'Entertainment',
                'id': 3
            }
        }

        res = self.client().post('/quizzes', json=test_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(
            data["message"], "Unprocessable: Server could not process your request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
