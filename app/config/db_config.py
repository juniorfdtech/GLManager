from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DBConnection:
    def __init__(self, uri: str = 'sqlite:///db.sqlite3') -> None:
        self.__uri = uri
        self.__engine = create_engine(self.__uri)
        self.__session = None

    @property
    def uri(self) -> str:
        return self.__uri

    @property
    def engine(self) -> create_engine:
        return self.__engine

    @property
    def session(self) -> sessionmaker:
        return self.__session

    def __enter__(self) -> 'DBConnection':
        self.__session = sessionmaker()(bind=self.engine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.session.close()
