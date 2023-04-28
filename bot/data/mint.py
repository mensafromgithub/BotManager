import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Mint(SqlAlchemyBase):
    __tablename__ = 'mint'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    cipher_key = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    bot = orm.relationship("Bots", back_populates='mint')
    answers = orm.relationship("Ans", back_populates='mint')