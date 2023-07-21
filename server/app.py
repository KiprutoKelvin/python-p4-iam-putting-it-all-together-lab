#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
     def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        bio = data.get('bio')
        image_url = data.get('image_url')

        if not all([username, password]):
            return {'message': 'Username and password are required.'}, 422

        try:
            new_user = User(username=username, bio=bio, image_url=image_url)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return {'message': 'User created successfully.'}, 201
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Username already exists.'}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return {'id': user.id, 'username': user.username}
        return {'message': 'Unauthorized.'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return {'message': 'Username and password are required.'}, 422

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return {'username': user.username}, 200

        return {'message': 'Invalid username or password.'}, 401

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return {'message': 'Logged out successfully.'}, 200

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            recipes = Recipe.query.filter_by(user_id=user_id).all()
            recipe_list = [{'title': r.title, 'instructions': r.instructions,
                            'minutes_to_complete': r.minutes_to_complete} for r in recipes]
            return recipe_list, 200
        return {'message': 'Unauthorized.'}, 401

    def post(self):
        user_id = session.get('user_id')
        if user_id:
            data = request.get_json()
            title = data.get('title')
            instructions = data.get('instructions')
            minutes_to_complete = data.get('minutes_to_complete')

            if not all([title, instructions, minutes_to_complete]):
                return {'message': 'Title, instructions, and minutes_to_complete are required.'}, 422

            new_recipe = Recipe(title=title, instructions=instructions, minutes_to_complete=minutes_to_complete, user_id=user_id)
            db.session.add(new_recipe)
            db.session.commit()
            return new_recipe.to_dict(), 201
        return {'message': 'Unauthorized.'}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
