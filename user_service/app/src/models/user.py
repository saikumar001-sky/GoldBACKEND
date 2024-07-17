from sqlalchemy import Column, Integer, String, DateTime
from src.core.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50),unique=True,nullable=False,index=True)
    password = Column(String(100))
    full_name = Column(String(200))
    email_id = Column(String(50))
    mobile_number = Column(String(20),unique=False)
    password_modified_date = Column(DateTime)
    created_by = Column(String(30))
    created_date = Column(DateTime)
    modified_by = Column(String(30))
    modified_date = Column(DateTime)
