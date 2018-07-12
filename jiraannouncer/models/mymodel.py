from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    BigInteger,
    JSON,
)

from .meta import Base


class JIRAMessage(Base):
    __tablename__ = 'jiramessage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(BigInteger)
    event = Column(Text)
    user = Column(JSON)
    issue = Column(JSON)
    changelog = Column(JSON)


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)


Index('my_index', MyModel.name, unique=True, mysql_length=255)
