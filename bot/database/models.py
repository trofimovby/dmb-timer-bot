from sqlalchemy import Column, BigInteger, String, Date, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)  # <-- Исправлено
    role = Column(String)
    enlist_date = Column(Date)
    discharge_date = Column(Date)
