import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','root','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            "question": "Quel est la capitale du Benin ?",
            "answer": "Porto-Novo",
            "category": 3,
            "difficulty": 2
        }
        
        self.new_invalid_question = {
            "question": "",
            "answer": "",
            "category": 2,
            "difficulty": 1
        }
        
        self.new_quizzes = {
            "previous_questions": [24],
            "quiz_category": {
                "type":"History",
                "id": "4"
            }
        }
        
        self.new_invalid_quizzes = {
            "previous_questions": [],
            "quiz_category": {"type":"adsb", "id": "10"}
        }
        
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    # Writing at least one test for each test for successful operation and for expected errors.
    
    # Testing retrieves categories successfully
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
    
    # Testing when retrieving categories failed
    def test_404_get_categories(self):
        res = self.client().get("/categories/2")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
        
    # Testing retrieves questions successfully
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["current_category"])
    
    # Testing when retrieving questions failed    
    def test_404_get_paginated_questions(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    # Testing delete question functionality
    def test_delete_question(self):
        res = self.client().delete("/questions/20")
        data = json.loads(res.data)
        
        question = Question.query.filter(Question.id == 20).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 20)
        self.assertTrue(data["questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)
    
    # Testing a case user attempt to delete nonexisting question
    def test_422_delete_question(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")
    
    # Testing the new question add functionality
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(len(data["questions"]))

    # The provided data from user must be valid, otherwise, failed creation
    def test_422_create_new_invalid_question(self):
        res = self.client().post("/questions", json=self.new_invalid_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
      
    # When user attempt to create new question providing invalid url
    def test_405_create_new_question_not_allowed(self):
        res = self.client().post("/questions/4", json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")
    
    # Testing search question functionality
    def test_search_question(self):
        res = self.client().post("/questions", json={"searchTerm":"title"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(len(data["questions"]))
    
    # We'll return null when user's search term can't be found
    def test_search_question_without_result(self):
        res = self.client().post('/questions', json={"searchTerm":"xlikouy"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'], [])
        self.assertEqual(data['total_questions'], 0)
    
    # But, since the search term can't be null, we raise an error if search term is null
    def test_422_search_question(self):
        res = self.client().post("/questions", json={"searchTerm":""})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
        
    # Testing retrieve questions within a category
    def test_get_questions_by_category(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
    
    # The category's id must be valid, otherwise, we raise an error
    def test_404_not_found_questions_by_category(self):
        res = self.client().get('/categories/200/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
    
    # Testing add quizzes functionality
    def test_playing_game(self):
        res = self.client().post('/quizzes', json=self.new_quizzes)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['question'])
    
    # Failed quizzes creation when providing empty data
    def test_422_unprocessable_playing_game(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")
     
    # Failed quizzes creation when providing invalid data   
    def test_422_unprocessable_playing_game_when_providing_invalid_category(self):
        res = self.client().post('/quizzes', json=self.new_invalid_quizzes)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")
         
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()