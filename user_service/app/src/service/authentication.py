import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models.user import User
from src.service.utils import verify_password


logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)-s:%(message)s')
logger = logging.getLogger(__name__)



# Use the hexadecimal string as the JWT secret key
    
async def authenticate_user(db:Session,user_name:str,password:str):
        try:
            logger.info(f"user_name: {user_name}===password:{password}")
            exist_user = db.query(User).filter(or_(User.user_name == user_name,User.email_id==user_name)).first()
            if exist_user:
                if verify_password(plain_password=password,hashed_password=exist_user.password):
                    return exist_user
                else:
                    return 2
            else:
                return 3
        except Exception as e:
            logger.info(f"Error occurred  in authenticate_user:{e}")



    




