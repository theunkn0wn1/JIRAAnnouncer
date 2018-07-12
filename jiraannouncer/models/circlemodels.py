from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    BigInteger,
    JSON,
)

from .meta import Base


class CircleMessage(Base):
    __tablename__ = 'circlemessage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(BigInteger)
    payload = Column(JSON)


Index('circle_idx', CircleMessage.id, unique=True)
