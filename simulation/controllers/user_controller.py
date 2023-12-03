from flask import Blueprint, request

from services.user_service import UserService


class UserController:
    user_controller = Blueprint('user', __name__)
    user_service = UserService()

    @staticmethod
    @user_controller.route('/user', methods=['POST'])
    def create_user():
        if request.method == 'POST':
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            UserController.user_service.add_user(name, email)
            return {'message': 'User added successfully'}, 201