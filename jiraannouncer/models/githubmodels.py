from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    BigInteger,
    JSON,
)

from .meta import Base


class GitHubMessage(Base):
    __tablename__ = 'githubmessage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(BigInteger)
    action = Column(Text)
    number = Column(Integer)
    issue = Column(JSON)
    comment = Column(JSON)
    repository = Column(JSON)
    organization = Column(JSON)
    sender = Column(JSON)
    pull_request = Column(JSON)
    changes = Column(JSON)


Index('github_idx', GitHubMessage.id, unique=True)
