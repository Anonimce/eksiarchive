
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import relationship

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"), pool_size=32, max_overflow=0)


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)

class Entry(DeclarativeBase):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    title_id = Column(Integer, ForeignKey('titles.id'))
    content = Column(String(10000000))
    likes = Column(Integer)
    date = Column(Date)

    author = relationship('Author', uselist=False, lazy=True, primaryjoin='Author.id == Entry.author_id')

    def __repr__(self):
        return '<Entry {} {}>'.format(self.id, self.content)

class Title(DeclarativeBase):
    __tablename__ = 'titles'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

class Author(DeclarativeBase):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    def __repr__(self):
        return '<Author {} {}>'.format(self.id, self.name)