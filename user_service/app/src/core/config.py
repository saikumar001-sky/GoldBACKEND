
import os
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, validator

class Settings(BaseSettings):
    API_V1_STR:Optional[str]
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    API_PREFIX = '/user'

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME:Optional[str]
    
    REDIRECT_CHANGE_PASSWORD_URL_ADMIN:Optional[str]
    REDIRECT_LOGIN_URL_ADMIN:Optional[str]
    
    SQLALCHEMY_DATABASE_URI:Optional[str]
    
    SUCCESS:str="Success"
    FAILED:str="Failed"

    class Config:
        case_sensitive = True

settings = Settings()
