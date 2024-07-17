from sqlalchemy import Column, Integer, String, DateTime,Date,ForeignKey,Float,Boolean
from src.core.base_class import Base

class Payment(Base):
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("client.id"))
    payment_number= Column(String(40),unique=True,index=True)
    rate = Column(Float)
    amount = Column(Float)
    gold_gain = Column(Float)
    date_of_payment = Column(Date)
    no_of_notification_sent = Column(Integer)
    is_notification_sent = Column(Boolean)
    notified_date = Column(DateTime)
    is_delete = Column(Boolean)
    created_by = Column(String(30))
    created_date = Column(DateTime)
    modified_by = Column(String(30))
    modified_date = Column(DateTime)