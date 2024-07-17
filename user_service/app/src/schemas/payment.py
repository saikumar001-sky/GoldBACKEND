from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

class PaymentBase(BaseModel):
    client_id:int
    rate:float
    amount:float
    gold_gain:float
    date_of_payment:date

class PaymentInDB(PaymentBase):
    id :Optional[int]
    payment_number:Optional[str]
    no_of_notification_sent:Optional[int]
    is_notification_sent:Optional[bool]
    notified_date:Optional[datetime]
    is_delete:Optional[bool]    
    created_by:Optional[str]
    created_date:Optional[datetime]
    modified_by:Optional[str]
    modified_date:Optional[datetime]
    
    class Config:
        orm_mode = True 