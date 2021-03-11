from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


engine = create_engine('sqlite:///sqlite3.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Session.configure(bind=engine)

Base = declarative_base()


class CurList(Base):
    __tablename__ = 'latest_currency_list'
    id = Column(Integer, primary_key=True)
    currency = Column(String)
    rate = Column(Integer)
    seen = Column(DateTime)

    def __init__(self, currency, rate):
        self.currency = currency
        self.rate = rate
        self.seen = datetime.now()

    def __str__(self):
        return "Currency:('%s','%s', '%s')" % (self.currency, self.rate, self.seen)


Base.metadata.create_all(engine)
