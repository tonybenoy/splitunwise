import datetime
from decimal import Decimal

from sqlalchemy import (
    ARRAY,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/split"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class BaseMixin(Base):
    __abstract__ = True

    def as_dict(self, datetime_to_str=True, columns=[]):
        columns = columns if columns else self.__table__.columns.keys()
        return {
            column_name: getattr(self, column_name).isoformat()
            if isinstance(getattr(self, column_name), datetime) and datetime_to_str
            else float(getattr(self, column_name))
            if isinstance(getattr(self, column_name), Decimal)
            else getattr(self, column_name)
            for column_name in columns
        }


class User(BaseMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))


class Expense(BaseMixin):
    __tablename__ = "expense"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric, nullable=False)
    user_ids = Column(ARRAY(Integer))
    paid_by = Column(Integer, ForeignKey(User.id), nullable=False)


class Split(BaseMixin):
    __tablename__ = "split"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey(Expense.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    amount = Column(Numeric, nullable=False)


class Payment(BaseMixin):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    amount = Column(Numeric, nullable=False)
    paid_to = Column(Integer, ForeignKey(User.id), nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
