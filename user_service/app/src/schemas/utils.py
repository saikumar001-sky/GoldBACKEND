from typing import Optional
from pydantic import BaseModel

class Generic_Response(BaseModel):
    message:Optional[str]
    data:Optional[list] = []
    status_code:Optional[int] = 200
    success:Optional[bool] = True