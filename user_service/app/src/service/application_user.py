import base64
from datetime import datetime, timedelta
import logging
from typing import Any, Optional, Union
from db_model.application_user import Application_User
from db_schema.customer.customer_login import CustomerLoginBase, CustomerLoginBaseInDB,CustomerLoginMobileBase
from db_schema.customer.customer_utils import PasswordHistory
from db_schema.enumes import UserStatus,RegistrationStatus
from src.service import utils
from db_handler.crud.user.crud_customer import application_user
from config.mail_config import settings as mail_config
from sqlalchemy.orm import Session
import config.jwt_config as jwt_config
import config.redis_config as redis_config 
import config.response_msg as appconfig
from jose import JWTError, jwt
import redis
from src.service import authentication
from helper.generate_otp import send_link_mobile
from db_handler.crud.setup.crud_password_format import pass_format
from db_handler.crud.user.crud_customer_utils import password_history
from db_schema.customer.session import SessionCreate
from db_handler.crud.user.crud_session import user_session

redis_client = redis.from_url(redis_config.REDIS_URL)

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)-s:%(message)s')
logger = logging.getLogger(__name__)


def crud_access_token(
                    db:Session,
                    user:Application_User,
                    ip: str = None,
                    headers: dict = None,
                    expires_delta:timedelta = timedelta(minutes=jwt_config.JWT_EXPIRATION_TIME_MINUTES)):
    logger.info(f"crud_access_token is trigger : {user.user_name if user else None}")
    try:
        browser = headers.get(appconfig.HEADER_USER_AGENT, None)
        exp: datetime = datetime.utcnow()+timedelta(hours=8) + expires_delta
        to_encode = {
                    appconfig.JWT_EXPIRY: exp,
                    appconfig.JWT_USERNAME: user.user_name
                    }
        encoded_jwt = jwt.encode(to_encode,jwt_config.JWT_SECRET_KEY,
                                algorithm=jwt_config.JWT_ALGORITHM)

        return encoded_jwt
    except Exception as e:
        logger.exception(f"Error occured in crud_access_token : {e}")
        
        


async def token(db:Session,
          username:str,
          password:str,
          redis:Any,
          ip:str) -> Optional[Union[str,int]]:
    logger.info(f"token is trigger: {username}")
    try:
        user = authenticate_user(db=db,username=username,password=password)
        logger.info(f"@@@@@@>>>{user}")
        if isinstance(user,int):
            logger.info(f"INTTTTTTTT{user}")
            return user
        elif isinstance(user, Application_User):
                ref_token = await authentication.get_refresh_token(redis_client=redis,username=username)
                logger.info(f"ref_token:777{ref_token}")
                if ref_token is None:
                    logger.info(f"ref_token:777NONE{ref_token}")
                    ref_token = await authentication.create_refresh_token(redis_client=redis, username=username)
                    logger.info(f"ref_token:777NONE888{ref_token}")
                else:
                    logger.info(f"ref_token:777NOTNONE{ref_token}")
                    ref_token = ref_token.access_token
                acc_token=await authentication.create_access_token_from_refresh_token(redis_client=redis,refresh_token=ref_token)
                logger.info(f"acc_token:777{acc_token}")
                if acc_token and acc_token==2:
                    return acc_token
                user = await authentication.get_current_user(db=db,token=acc_token.access_token)
                if user and user==2:
                    return user
                elif user:
                    return redis_client.get(f"acc{username}")
    except Exception as e:
        logger.exception(f"Error occured in token : {e}")


def authenticate_user(db:Session,
                      username:str,
                      password:str) -> Optional[Union[Application_User,int]]:
    logger.info(f"authenticate_user is trigger: {username}")
    try:
        user=None
        user = application_user.get_customer_by_user_id(db=db,user_id=username)
        logger.info(f"user: {user}")
        if user:
            login_wrong_attempts = user.login_wrong_attempts
            if user.is_locked:
                logger.info(f"User Locked : {username}")
                return 3
            elif not utils.verify_hash(password, user.password):
                logger.info(f"Password Missmatched: {username}")
                login_wrong_attempts = login_wrong_attempts+1 if login_wrong_attempts else 1
                is_locked=False
                if user.login_wrong_attempts:
                    format_data = pass_format.get_data(db=db)
                    if user.login_wrong_attempts > (format_data.wrong_login_attempts_limit if format_data else 3):
                        is_locked = True
                        authentication.delete_token(redis_client=redis_client,username=username)
                application_user.update(db=db,db_obj=user,obj_in={'login_wrong_attempts':login_wrong_attempts,
                                                                'is_locked':is_locked,
                                                                'locked_reason':"Attempted consecutive wrong password attempts." if is_locked else None,
                                                                'locked_date':datetime.utcnow()+timedelta(hours=8) if is_locked else None})
                return 4
            else:
                logger.info(f"User Found: {username}")
                last_login_date = user.current_login_date
                current_login_date = datetime.utcnow()+timedelta(hours=8)
                login_wrong_attempts = 0
                application_user.update(db=db,db_obj=user,obj_in={'login_wrong_attempts':login_wrong_attempts,
                                                                    'last_login_date':last_login_date,
                                                                    'current_login_date':current_login_date})
                return user
        else:
            logger.info(f"User Not Found : {username}")
            return 1
    except Exception as e:
        logger.exception(f"Error occurred in authenticate_user : {e}")



def get_current_user(db:Session,token: str) -> Optional[Application_User]:
    logger.info("get_current_user is trigger")
    try:
        payload = jwt.decode(token,jwt_config.JWT_SECRET_KEY,
                             algorithms=[jwt_config.JWT_ALGORITHM])
        if payload:
            username: str = payload.get(appconfig.JWT_USERNAME)
            if username:
                user=None
                user = application_user.get_customer_by_user_id(db=db,user_id=username)
                if user:
                    acc_token = redis_client.get(f"acc{username}")
                    if acc_token is not None and acc_token.decode('utf-8') == payload:
                        application_user.update(db=db,db_obj=user,obj_in={'last_login_date':user.current_login_date,
                                                                            'current_login_date':datetime.utcnow()+timedelta(hours=8)})
                        return user
    except JWTError as e:
        logger.exception(f"Error occurred in get_current_user: {e}")


def register_user_basic_data(db:Session,
                             payload:Union[CustomerLoginBase,CustomerLoginMobileBase],
                             ip_address)->Optional[Application_User]:
    logger.info(f"register_user_basic_data service : {payload}=={ip_address}")
    try:
        user=None
        if isinstance(payload,CustomerLoginBase):
            user = CustomerLoginBaseInDB(
                user_name= payload.user_name,
                email_id= payload.user_name,
                password=utils.generate_hash(str(payload.password)),
                created_date=datetime.utcnow()+timedelta(hours=8),
                ip_address=ip_address,
                is_email_confirmation=True,
                two_factor_enabled=True,
                email_verified_date=datetime.utcnow()+timedelta(hours=8),
                user_status=UserStatus.DRAFT,
                registration_status=RegistrationStatus.ON_HOLD,
                language=appconfig.USER_LANGUAGE   
            ) 
        if isinstance(payload,CustomerLoginMobileBase): 
            user = CustomerLoginBaseInDB(
                user_name=payload.user_email,
                email_id=payload.user_email,
                mobile_number= payload.mobile_number,
                password=utils.generate_hash(str(payload.password)),
                created_date=datetime.utcnow()+timedelta(hours=8),
                ip_address=ip_address,
                is_mobile_confirmation=True,
                two_factor_enabled=True,
                mobile_verified_date=datetime.utcnow()+timedelta(hours=8),
                user_status=UserStatus.DRAFT,
                registration_status=RegistrationStatus.ON_HOLD,
                language=appconfig.USER_LANGUAGE   
            )
        if user:             
            data=application_user.create(db=db,obj_in=user)
            return data
    except Exception as e:
        logger.exception(f"Error occurs in register_user_basic_data: {e}")
        
        
        
def logout(db:Session,user:Application_User,redis:Any) -> Optional[bool]:
    logger.info("logout is trigger")
    try:
        redis.delete(f"ref{user.user_name}")
        redis.delete(f"acc{user.user_name}")
        return True
    except Exception as e:
        logger.exception(f"Error occurred in logout : {e}")


def update_password(db:Session,
                    password:str,
                    ip:str,
                    headers:dict,
                    user:Application_User) -> Optional[int]:
    logger.info("update_password is trigger")
    try:
        pwd_history = password_history.get_last_three_passwords(db=db,user_id=user.user_id)
        is_old_password = False
        if utils.verify_hash(password,user.password):
            is_old_password = True
        if pwd_history and not is_old_password:
            for old_password in pwd_history:
                if utils.verify_hash(password,old_password.password):
                    is_old_password = True
                    break
        if is_old_password:
            return 1
        else:
            password_modified_date=datetime.utcnow()+timedelta(hours=8)
            password_data = PasswordHistory(
                                    user_id=user.user_id,
                                    password=user.password,
                                    created_date=password_modified_date,
                                    pwd_exp_date=datetime.utcnow()+timedelta(days=30),
                                    is_active=True)
            password_history.create(db=db,obj_in=password_data)
            application_user.update_data(db=db,login_id=user.login_id,data={'password':utils.generate_hash(password),
                                                                                'password_modified_date':password_modified_date})                
            return 0
    except Exception as e:
        logger.exception(f"Error occurred in update_password : {e}")
        
        


def encode_reset_password_link(user:Application_User,modified_date:datetime) -> str:
    logger.info("encode_reset_password_link is trigger")
    try:
        text = f"{user.user_id}~{modified_date.timestamp()}"
        return mail_config.EMAIL_BODY_HOST.rstrip(
            '/') + appconfig.API_V1 + appconfig.API_PREFIX + appconfig.RESET_PASSWORD_API + '/' + base64.b64encode(
            text.encode(appconfig.ENCODING_UTF8)).decode(appconfig.ENCODING_UTF8)
    except Exception as e:
        logger.exception(f"Error occurred in encode_reset_password_link : {e}")


def encode_reset_password_mobile_link(user:Application_User,modified_date:datetime) -> str:
    logger.info("encode_reset_password_mobile_link is trigger")
    try:
        text = f"{user.user_id}~{modified_date.timestamp()}"
        return mail_config.EMAIL_BODY_HOST.rstrip(
            '/') + appconfig.API_V1 + appconfig.API_PREFIX + appconfig.RESET_PASSWORD_API + '/' + base64.b64encode(
            text.encode(appconfig.ENCODING_UTF8)).decode(appconfig.ENCODING_UTF8)
    except Exception as e:
        logger.exception(f"Error occurred in encode_reset_password_mobile_link : {e}")



def decode_reset_password_link(text: str,db:Session) -> Application_User:
    logger.info("decode_reset_password_link is trigger")
    try:
        decoded = base64.b64decode(text).decode()
        user_id, modified_time = decoded.split('~')
        db_user = application_user.get_customer_by_user_id(db=db,user_id=user_id)
        if db_user.user_id == user_id and round(
            db_user.modified_date.timestamp()) == round(float(modified_time)):
            return db_user
    except Exception as e:  # Failed to decode
       logger.exception(f"Error occurred in decode_reset_password_link : {e}")
       
       
def decode_reset_password_mobile_link(text: str,db:Session) -> Application_User:
    logger.info("decode_reset_password_mobile_link is trigger")
    try:
        decoded = base64.b64decode(text).decode()
        user_id, modified_time = decoded.split('~')
        logger.info(f"decoded:{decoded}===mobile:{user_id}====modified_time:{modified_time}")
        db_user = application_user.get_customer_by_user_id(db=db,user_id=user_id)
        logger.info(f"db_user: {db_user}")
        if db_user:
            logger.info(f"db_user.modified_date.timestamp():{db_user.link_confirmation_date.timestamp()}===modified_time:{modified_time}")
            if db_user.user_id == user_id and round(
                db_user.link_confirmation_date.timestamp()) == round(float(modified_time)):
                return db_user
    except Exception as e:  # Failed to decode
       logger.exception(f"Error occurred in decode_reset_password_mobile_link : {e}")
       
       

async def reset_password(mobile:str,
                         db:Session,
                         user_type:Optional[str]="USR") -> Optional[bool]:
    logger.info("reset_password is trigger")
    try:
        db_user = application_user.get_customer_by_mobile_user_type(db=db,mobile=mobile,user_type=user_type)
        logger.info(f"db_user: {db_user}")
        if db_user:
            modified_date = datetime.utcnow()
            link = encode_reset_password_mobile_link(user=db_user,modified_date=modified_date)
            link_template=await send_link_mobile(to_mobile=db_user.mobile_number,name=db_user.full_name,link=link)  
            if link_template:    
                application_user.update_data(db=db,data={'link_confirmation_date':modified_date,
                                                            'is_link_confirmation':False},login_id=db_user.login_id)
                return link_template
    except Exception as e:
        logger.exception(f"Error occured in reset_password:{e}")
        
        
def reset_password_confirmation(token_data, ip,headers,db:Session) -> Optional[Application_User]:
    logger.info("reset_password_confirmation is trigger")
    try:
        if token_data:
            db_user = decode_reset_password_mobile_link(text=token_data,db=db)
            if db_user:
                logger.info(f"db_user:{db_user}")
                user = application_user.update_data(db=db,data={'force_change_password':True,
                                                                     'is_locked':False,
                                                                     'link_confirmation_date':datetime.utcnow()+timedelta(hours=8),
                                                                     'is_link_confirmation':True},
                                                         login_id=db_user.login_id)
                return user
    except Exception as e:
        logger.exception(f"Error occured in reset_password_confirmation : {e}")
        
def check_session(db:Session,
                session:SessionCreate):
    try:
        active_session=user_session.get_session_active_session(db=db,login_id=session.login_id)
        logger.info(f"session: {session.device_id}==={active_session.device_id if active_session else None}")
        if active_session and active_session.device_id == session.device_id:
            return 1
        elif active_session:
            return 2
        else:
            data = user_session.create(db=db,obj_in=session)
            if data:
                user_session.update_status(db=db,data={'is_active':False},id=data.id,login_id=data.login_id)
                return 1
    except Exception as e:
        logger.info(f"Error occurred in check_session: {e}")
        
        
