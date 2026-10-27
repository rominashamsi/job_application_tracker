from datetime import date
from .database import Base
from sqlalchemy import Integer, String , Text, Date, ForeignKey
from sqlalchemy.orm import mapped_column , relationship



class User(Base):
    __tablename__ = "users"
    id  =mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    email = mapped_column(String(255), nullable=False, unique=True)
    hashed_password = mapped_column(String(255), nullable=False)

    job_applications = relationship ( "JobApplication", back_populates= "user")


class JobApplication(Base):
    __tablename__ = "job_applications"
    id = mapped_column (Integer, primary_key=True)
    company = mapped_column (String(150), nullable=False)
    job_title = mapped_column (String(150), nullable=False)
    status = mapped_column (String(50), default = "applied" , nullable = False)
    job_url = mapped_column (String(500), nullable = True)
    notes = mapped_column ( Text , nullable= True)
    applied_date = mapped_column (Date, default= date.today,nullable= False)
    user_id = mapped_column ( Integer, ForeignKey("users.id"), nullable = False)
    user = relationship ("User", back_populates = "job_applications")
    salary = mapped_column (Integer, nullable=True)