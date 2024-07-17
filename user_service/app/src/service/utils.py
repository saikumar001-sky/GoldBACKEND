import logging
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from starlette import status
from src.schemas.utils import Generic_Response

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)-s:%(message)s')
logger = logging.getLogger(__name__)
         
encrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")        
def generate_hash(plain_text: str) -> str:
        return encrypt.hash(plain_text)        
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_response(code=status.HTTP_200_OK, message:Optional[str]=None, data=[])->Optional[Generic_Response]:
        logger.info("generate_response is trigger")
        try:
          return Generic_Response(status_code=code,
                                          data=data,
                                          message=message,
                                          success=True if (code==200 or code==201 or code==0) else False)
        except Exception as e:
            logger.exception(f"Error occurred in generate_response:{e}")


        
