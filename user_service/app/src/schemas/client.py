from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from src.schemas.enumes import Gender,MartialStatus

class ClientBase(BaseModel):
    first_name:str
    last_name:str
    gender:Gender
    dob:date
    martial_status:MartialStatus
    marriage_date:Optional[date]
    spouse_name:Optional[str]
    spouse_mobile_number:Optional[str]
    spouse_adhaar_number:Optional[str]
    email_id:Optional[str]
    mobile_number:Optional[str]
    alter_mobile_number:Optional[str]
    adhaar_number:str
    address:str

    
class ClientInDB(ClientBase):
    id :Optional[int]
    client_id:Optional[str]
    full_name:Optional[str]
    created_by:Optional[str]
    created_date:Optional[datetime]
    modified_by:Optional[str]
    modified_date:Optional[datetime]
    
    class Config:
        orm_mode = True 