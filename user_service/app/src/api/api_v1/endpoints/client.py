from datetime import datetime, timedelta
from fastapi import Request,APIRouter,Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from src.core.deps import get_db
from src.models.client import Client
from src.schemas.client import ClientBase,ClientInDB
import logging
from src.service.utils import generate_response
from starlette import status
from src.core.config import settings
from src.models.payment import Payment

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)-s:%(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/add")
async def add_client(request: Request,
                    payload:ClientBase,
                    db:Session=Depends(get_db)):
    try:
        is_mobile = db.query(Client).filter(Client.mobile_number==payload.mobile_number).first()
        if is_mobile is None:
            client_id = 10000001
            last_client = db.query(Client).order_by(Client.id.desc()).first()
            if last_client:
                client_id = int(last_client.client_id[2:]) + 1
                
            data = ClientInDB(**payload.dict(),
                    client_id = str(f"{payload.first_name[0]}{payload.last_name[0]}{client_id}").strip().upper(),
                    full_name = str(f"{payload.first_name} {payload.last_name}").title().strip(),
                    created_by = "Admin",
                    created_date = datetime.utcnow()+timedelta(hours=5,minutes=30)
                        )
            data = Client(**data.dict())
            db.add(data)
            db.commit()
            db.refresh(data)
            if data:
                return generate_response(code=status.HTTP_200_OK,message=settings.SUCCESS,data=[jsonable_encoder(data)])
        return generate_response(code=status.HTTP_400_BAD_REQUEST,message=settings.FAILED)
    except Exception as e:
        logger.info(f"Error Occurred in  adding new client : {e}")
        return generate_response(code=status.HTTP_500_INTERNAL_SERVER_ERROR,message=settings.FAILED)


@router.get("/get")
async def get_clients(request: Request,
                      db:Session=Depends(get_db)):
    try:
        all_clients = db.query(Client).order_by(Client.client_id).all()
        response_data=[]
        if all_clients:
            for client in all_clients:
                data = ClientInDB(**jsonable_encoder(client,exclude_unset=True))
                data = data.dict()
                all_payments = db.query(Payment).filter(Payment.client_id==client.id).all()
                total_amount=0
                total_gold=0
                no_of_payments=0
                if all_payments:
                    for payment in all_payments:
                        total_amount = total_amount + payment.amount
                        total_gold = total_gold + payment.gold_gain
                        no_of_payments = no_of_payments + 1
                data.update({'total_amount':total_amount,
                             'total_gold':total_gold,
                             'no_of_payments':no_of_payments})
                response_data.append(data)
                
        return generate_response(code=status.HTTP_200_OK,message=settings.SUCCESS,data=jsonable_encoder(response_data))
    except Exception as e:
        logger.info(f"Error Occurred in  adding new client : {e}")
        return generate_response(code=status.HTTP_500_INTERNAL_SERVER_ERROR,message=settings.FAILED)
    
@router.get("/get/{client_id}")
async def get_clients(request: Request,
                      client_id:str,
                      db:Session=Depends(get_db)):
    try:
        client_data = db.query(Client).filter(Client.client_id==client_id).first()
        if client_data:
                data = ClientInDB(**jsonable_encoder(client_data,exclude_unset=True))
                data = data.dict()
                all_payments = db.query(Payment).filter(Payment.client_id==client_data.id).all()
                total_amount=0
                total_gold=0
                no_of_payments=0
                if all_payments:
                    for payment in all_payments:
                        total_amount = total_amount + payment.amount
                        total_gold = total_gold + payment.gold_gain
                        no_of_payments = no_of_payments + 1
                data.update({'total_amount':total_amount,
                             'total_gold':total_gold,
                             'no_of_payments':no_of_payments})
                return generate_response(code=status.HTTP_200_OK,message=settings.SUCCESS,data=[jsonable_encoder(data)])
        else:
            return generate_response(code=status.HTTP_404_NOT_FOUND,message=settings.FAILED)
    except Exception as e:
        logger.info(f"Error Occurred in  adding new client : {e}")
        return generate_response(code=status.HTTP_500_INTERNAL_SERVER_ERROR,message=settings.FAILED)
    
    
@router.put("/update/{client_id}")
async def update_client(request: Request,
                    client_id:str,
                    payload:ClientBase,
                    db:Session=Depends(get_db)):
    try:
        client_data = db.query(Client).filter(Client.client_id==client_id)
        if client_data.first():
            is_mobile = db.query(Client).filter(Client.mobile_number==payload.mobile_number).first()
            if is_mobile is None or is_mobile.mobile_number==payload.mobile_number:  
                data = payload.dict()  
                data.update({'full_name':str(f'{payload.first_name} {payload.last_name}').title().strip()})                 
                client_data.update(data)
                db.commit()
                return generate_response(code=status.HTTP_200_OK,message=settings.SUCCESS)
            return generate_response(code=status.HTTP_409_CONFLICT,message=settings.FAILED)
        else:
            return generate_response(code=status.HTTP_404_NOT_FOUND,message=settings.FAILED)
    except Exception as e:
        logger.info(f"Error Occurred in update_client: {e}")
        return generate_response(code=status.HTTP_500_INTERNAL_SERVER_ERROR,message=settings.FAILED)