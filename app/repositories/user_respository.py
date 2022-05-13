from app.config import DBConnection
from app.models import User
from app.dtos import UserDto

class UserRepository:
    @staticmethod
    def create(user_dto: UserDto) -> User:
        with DBConnection() as db:
            user = User(**user_dto.to_dict())
            db.session.add(user)
            db.session.commit()

    @staticmethod
    def get_by_id(id: int) -> User:
        with DBConnection() as db:
            return db.session.query(User).filter(User.id == id).first()

    @staticmethod
    def get_by_username(username: str) -> User:
        with DBConnection() as db:
            return db.session.query(User).filter(User.username == username).first()

    @staticmethod
    def get_all() -> list:
        with DBConnection() as db:
            return db.session.query(User).all()

    @staticmethod
    def update(id: int, user_dto: UserDto) -> User:
        with DBConnection() as db:
            user = db.session.query(User).filter(User.id == id).first()
            user.username = user_dto.username
            user.password = user_dto.password
            user.connection_limit = user_dto.connection_limit
            user.expiration_date = user_dto.expiration_date
            db.session.commit()
            return user

    @staticmethod
    def delete(id: int) -> None:
        with DBConnection() as db:
            user = db.session.query(User).filter(User.id == id).first()
            db.session.delete(user)
            db.session.commit()