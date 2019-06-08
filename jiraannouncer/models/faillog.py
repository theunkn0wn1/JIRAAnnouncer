from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    BigInteger
)

from .meta import Base


class FailLog(Base):
    __tablename__ = 'faillog'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(BigInteger)
    headers = Column(Text)
    endpoint = Column(Text)
    body = Column(Text)


Index('faillog_idx', FailLog.id, unique=True)
