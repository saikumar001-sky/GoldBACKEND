from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from src.core.base_class import Base
from src.core.deps import engine
from src.models.user import User
from src.service.utils import generate_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db:Session) -> None:
      # Create tables
      Base.metadata.create_all(engine)
      
      # Check if the user already exists
      existing_user = db.query(User).filter_by(user_name='anand').first()

      if existing_user is None:
            # Add a super user
            super_user = User(
            user_name='anand',
            password=generate_hash(plain_text='Anand123@@@'),
            full_name='Anand',
            email_id='anand@gmail.com',
            mobile_number='1234567890',
            created_by = "Admin",
            created_date =datetime.utcnow()+timedelta(hours=5,minutes=30)
            # Set other attributes as needed
            )

            # Add the super user to the session
            db.add(super_user)

            # Commit the changes to the database
            db.commit()
                        
