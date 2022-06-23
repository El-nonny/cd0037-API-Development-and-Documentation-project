import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_question(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    asked_questions = questions[start:end]

    return asked_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
    

        if len(categories) == 0:
            abort(404)
        
        return jsonify({
            "success": True,
            "categories": {catig.id: catig.type for catig in categories}
        })


    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        asked_questions = paginate_question(request, selection)

        if len(asked_questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": asked_questions,
            "total_questions": len(Question.query.all()),
            "categories": {catig.id: catig.type for catig in Category.query.all()}
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            asked_questions = paginate_question(request, selection)
            
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': asked_questions,
                'total_questions': len(selection)
            })

        except Exception:
            abort(422)

    @app.route("/questions", methods=["POST"])
    def create_book():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty_score = body.get("difficulty_score", None)

        try:
            questions = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty_score)
            questions.insert()

            selection = Question.query.order_by(Question.id).all()
            asked_questiona = paginate_question(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": questions.id,
                    "questions": asked_questiona,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)


    @app.route('/search', methods=['POST'])
    def search():
        body = request.get_json()
        search = body.get('searchTerm')
        selection = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
        asked_questiona = paginate_question(request, selection)
        
        if len(asked_questiona) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": asked_questiona,
            "total_questions": len(selection),
        })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        category = Category.query.filter(Category.id == category_id).first()
        selection = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
        asked_questions = paginate_question(request, selection)

        if len(asked_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': asked_questions,
            'total_questions': len(selection),
            'current_category': category.format()
        })

    @app.route('/quiz', methods=['POST'])
    def get_quizzes():
        # This endpoint should take category and previous question parameters
        try:
            body = request.get_json()
            quiz_categ = body.get('quiz_category', None)
            prev_questions = body.get('previous_questions', None)
            category_id = quiz_categ['id']

            if category_id == 0:
                questions = Question.query.filter(Question.id.notin_(prev_questions)).all()
            else:
                questions = Question.query.filter(Question.id.notin_(prev_questions),
                Question.category == category_id).all()
            question = None

            if(questions):
                question = random.choice(questions)

            return jsonify({
                'success': True,
                'question': question.format()
            })

        except Exception:
            abort(404)

            

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404, 
            "message": "resource not found"
            }), 404,

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422, 
            "message": "unprocessable"
            }), 422,

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400, 
            "message": "bad request"
            }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 405, 
            "message": "method not allowed"
            }), 405

    return app

