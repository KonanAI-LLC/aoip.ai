from data.user_repository import UserRepository


class UserService:

    def __init__(self):
        self.user_repo = UserRepository()

    def add_user(self, name, email):
        self.user_repo.add_user(name, email)