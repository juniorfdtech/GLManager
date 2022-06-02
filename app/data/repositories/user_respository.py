from app.data.config import DBConnection
from app.domain.entities import User


class UserRepository:
    @staticmethod
    def create(user: User) -> User:
        with DBConnection() as db:
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)

        return user

    @staticmethod
    def get_by_id(id: int) -> User:
        with DBConnection() as db:
            return db.session.query(User).filter(User.id == id).first()

    @staticmethod
    def get_by_username(username: str) -> User:
        if not username:
            raise ValueError('username is required')

        with DBConnection() as db:
            return db.session.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_uuid(uuid: str) -> User:
        if not uuid:
            raise ValueError('uuid is required')

        with DBConnection() as db:
            return db.session.query(User).filter(User.v2ray_uuid == uuid).first()

    @staticmethod
    def get_all() -> list:
        with DBConnection() as db:
            return db.session.query(User).all()

    @staticmethod
    def update(user: User) -> User:
        if not user.id:
            raise Exception('User id is required')

        with DBConnection() as db:
            db.session.merge(user)
            db.session.commit()

        return user

    @staticmethod
    def delete(id: int) -> User:
        with DBConnection() as db:
            user = db.session.query(User).filter(User.id == id).first()
            db.session.delete(user)
            db.session.commit()
            return user
