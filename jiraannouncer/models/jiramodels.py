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


Index('jira_idx', JIRAMessage.id, unique=True)
