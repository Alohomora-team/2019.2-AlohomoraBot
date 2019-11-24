"""
Models to persist chat_id
"""

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Resident(Base):
    """
    Saves a resident chat_id
    """

    __tablename__ = 'residents'

    id = Column(Integer, primary_key=True)
    cpf = Column(String(11), unique=True)
    apartment = Column(String(10))
    block = Column(String(10))
    chat_id = Column(Integer, unique=True)
    token = Column(Text)

class Visitor(Base):
    """
    Visitor models, saves chat_id
    """
    __tablename__ = 'visitors'

    id = Column(Integer, primary_key=True)
    cpf = Column(String(11), unique=True)
    chat_id = Column(Integer, unique=True)

class Admin(Base):
    """
    Save a admin chat_id
    """
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    email = Column(String(60), unique=True)
    chat_id = Column(Integer, unique=True)
    token = Column(Text)

engine = create_engine('sqlite:///../database.db')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
