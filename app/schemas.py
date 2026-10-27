from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Literal
from pydantic import Field



class UserCreate(BaseModel):
    name : str = Field(min_length=1, max_length=100)
    email : str = Field (min_length=3, max_length=255)
    password : str = Field(min_length= 8, max_length=128)


class UserLogin(BaseModel):
    email: str 
    password : str 


class UserResponse(BaseModel):
    id : int
    name : str
    email : str 


class Token(BaseModel):
    access_token : str
    token_type : str


class JobApplicationCreate(BaseModel):
    company : str 
    job_title : str 
    job_url : str | None = None
    notes : str | None = None
    salary: int | None = None

class JobApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes= True)

    id : int
    company : str 
    job_title :str
    status : str
    job_url : str | None = None
    notes : str | None = None
    applied_date : date
    salary: int | None


class JobApplicationUpdate(BaseModel):
    
    company: str | None = Field(default=None, min_length=1, max_length=150)
    job_title: str | None = Field(default=None, min_length=1, max_length=150)
    status: Literal["applied", "interview", "offer", "rejected"] | None = None
    job_url: str | None = Field(default=None, max_length=500)
    notes: str | None = None
    salary: int | None = Field(default=None, ge=0)

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
    



