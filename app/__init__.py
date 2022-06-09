import app.domain.entities
from app.data.config import Base, DBConnection

with DBConnection() as db:
    Base.metadata.create_all(db.engine)

import app.modules

__version__ = '0.0.1'
__author__ = 'Glemison C. DuTra'
__email__ = 'glemyson20@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022, Glemison C. DuTra'
