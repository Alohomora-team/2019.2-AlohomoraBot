from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Resident(Base):
    __tablename__ = 'residents'

    id = Column(Integer, primary_key=True)
    cpf = Column(String(11), unique=True)
    apartment = Column(String(10))
    block = Column(String(10))
    chat_id = Column(Integer, unique=True)

class Visitor(Base):
    __tablename__ = 'visitors'

    id = Column(Integer, primary_key=True)
    cpf = Column(String(11), unique=True)
    chat_id = Column(Integer, unique=True)

class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    email = Column(String(60), unique=True)
    chat_id = Column(Integer, unique=True)

engine = create_engine('sqlite:///./database.db')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
