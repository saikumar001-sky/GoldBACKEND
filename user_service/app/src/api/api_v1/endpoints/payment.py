from datetime import datetime, timedelta
import random
from fastapi import Request,APIRouter,Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from src.core.deps import get_db
from src.models.client import Client
from src.models.payment import Payment
from src.schemas.payment import PaymentBase,PaymentInDB
import logging
from src.service.utils import generate_response
from starlette import status
from src.core.config import settings

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)-s:%(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/add")
async def add_payment(request: Request,
                    payload:PaymentBase,
                    db:Session=Depends(get_db)):
    try:
        client_data = db.query(Client).filter(Client.id==payload.client_id).first()
        if client_data:
            payment_number=None
            while(True):
                payment_number = "ADJTXN"+str(random.randint(10**9, (10**10)-1))
                if_payment_number = db.query(Payment).filter(Payment.payment_number==payment_number).first()
                if if_payment_number:
                    continue
                else:
                    break
            if payment_number:    
                data = PaymentInDB(**payload.dict(),
                        payment_number=payment_number,
                        created_by = "Admin",
                        created_date = datetime.utcnow()+timedelta(hours=5,minutes=30)
                            )
                data = Payment(**data.dict())
                db.add(data)
                db.commit()
                db.refresh(data)
                if data:
                    return generate_response(code=status.HTTP_200_OK,message=settings.SUCCESS,data=[jsonable_encoder(data)])
        return generate_response(code=status.HTTP_400_BAD_REQUEST,message=settings.FAILED)
    except Exception as e:
        logger.info(f"Error Occurred in  adding add_payment : {e}")
        return generate_response(code=status.HTTP_500_INTERNAL_SERVER_ERROR,message=settings.FAILED)
    
    
@router.get("/get/{client_id}")
async def get_payments(request: Request,
                      client_id:str,  
                      db:Session=Depends(get_db)):
    try:
        client_data = db.query(Client).filter(Client.client_id==client_id).first()
        logger.info(f"client_data=========>${client_data.id}")
        if client_data:
            all_payments = db.query(Payment).filter(Payment.client_id==client_data.id).all()
            payment_data=[]
            if all_payments:
                total_amount=0
                total_gold=0
                no_of_payments=0
                
                for payment in all_payments:
                    payment_data.append({
                        'id':payment.id,
                        'payment_number':payment.payment_number,
                        'date_of_payment':payment.date_of_payment,
                        'rate':payment.rate,
                        'amount':payment.amount,
                        'gold': payment.gold_gain
                    })
                    total_amount = total_amount + payment.amount
                    total_gold = total_gold + payment.gold_gain
                    no_of_payments = no_of_payments + 1
                response_data={
                        'client_id':client_data.client_id,
                        'adhaar_number':client_data.adhaar_number,
                        'client_name':client_data.full_name,
                        'total_amount':total_amount,
                        'total_gold':total_gold,
                        'no_of_payments':no_of_payments,
                        'payment_list':payment_data
                }
                return generate_response(code=status.HTTP_200_OK,message=settings.SUCCESS,data=[jsonable_encoder(response_data)])
        else:
            return generate_response(code=status.HTTP_404_NOT_FOUND,message=settings.FAILED)
    except Exception as e:
        logger.info(f"Error Occurred in  get all payments : {e}")
        return generate_response(code=status.HTTP_500_INTERNAL_SERVER_ERROR,message=settings.FAILED)
    
@router.get("/get-payment/{payment_id}")
async def get_payment_by_id(request: Request,
                      payment_id:int,
                      db:Session=Depends(get_db)):
    try:
        payment_data = db.query(Payment).filter(Payment.id==payment_id).first()
        if payment_data:
            client_data = db.query(Client).filter(Client.id==payment_data.client_id).first()
            data = {
                    'client_id':client_data.client_id,
                    'adhaar_number':client_data.adhaar_number,
                    'client_name':client_data.full_name,
                    'mobile_number':client_data.mobile_number,
                    'email':client_data.email_id,
                    'address':client_data.address,
                    'payment_number':payment_data.payment_number,
                    'date_of_payment':payment_data.date_of_payment,
                    'rate':payment_data.rate,
                    'amount':payment_data.amount,
                    'gold': payment_data.gold_gain
                    }
            return generate_response(code=status.HTTP_200_OK,message=settings.SUCCESS,data=[jsonable_encoder(data)])
        else:
            return generate_response(code=status.HTTP_404_NOT_FOUND,message=settings.FAILED)
    except Exception as e:
        logger.info(f"Error Occurred in  adding new client : {e}")
        return generate_response(code=status.HTTP_500_INTERNAL_SERVER_ERROR,message=settings.FAILED)