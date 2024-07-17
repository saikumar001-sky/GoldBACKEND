from fastapi import Request,APIRouter,Depends
from fastapi.encoders import jsonable_encoder
from src.service.authentication import authenticate_user
from sqlalchemy.orm import Session
from src.core.deps import get_db
from src.schemas.user import LoginBase
import logging
from src.service.utils import generate_response,generate_hash
from starlette import status
from src.core.config import settings
from src.models.user import User
from sqlalchemy import or_

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)-s:%(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login")
async def admin_login(request: Request,
                      payload:LoginBase,
                      db:Session=Depends(get_db)):
    try:
        is_user = await authenticate_user(db=db,user_name=payload.user_name,password=payload.password)
        if is_user and isinstance(is_user,User):
            return generate_response(code=status.HTTP_200_OK,message=settings.SUCCESS,data=[{'user_name':is_user.full_name,
                                                                                             'id':is_user.id}])
        else:
            return generate_response(code=status.HTTP_401_UNAUTHORIZED,message=settings.FAILED)
    except Exception as e:
        logger.info(f"Error in login: {e}")
        return generate_response(code=status.HTTP_500_INTERNAL_SERVER_ERROR,message=settings.FAILED)
    
@router.get("/get/{id}")
async def get_profile(request: Request,
                      id:int,
                      db:Session=Depends(get_db)):
    try:
        is_user = db.query(User).filter(User.id==id).first()
        if is_user:
            return generate_response(code=status.HTTP_200_OK,message=settings.SUCCESS,data=[jsonable_encoder(is_user)])
        else:
            return generate_response(code=status.HTTP_404_NOT_FOUND,message=settings.FAILED)
    except Exception as e:
        logger.info(f"Error in login: {e}")
        return generate_response(code=status.HTTP_500_INTERNAL_SERVER_ERROR,message=settings.FAILED)
    
    
@router.post("/forgot-password")
async def forgot_password(request: Request,
                      payload:LoginBase,
                      db:Session=Depends(get_db)):
    try:
        is_user = db.query(User).filter(or_(User.email_id==payload.user_name,User.user_name==payload.user_name))
        if is_user.first():
            is_user.update({'password':generate_hash(payload.password)})
            db.commit()
            return generate_response(code=status.HTTP_200_OK,message=settings.SUCCESS)
        else:
            return generate_response(code=status.HTTP_401_UNAUTHORIZED,message=settings.FAILED)
    except Exception as e:
        logger.info(f"Error in forgot_password: {e}")
        return generate_response(code=status.HTTP_500_INTERNAL_SERVER_ERROR,message=settings.FAILED)
