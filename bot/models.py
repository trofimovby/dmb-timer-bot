from sqlalchemy import Column, BigInteger, String, Date, Boolean

from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    role = Column(String)
    enlist_date = Column(Date)
    discharge_date = Column(Date)

    is_subscribed = Column(Boolean, default=True, nullable=False)
    notify_mode = Column(String, default="key_dates")  # 'key_dates' или 'weekly'