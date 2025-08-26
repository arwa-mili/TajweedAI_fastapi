import json
from fastapi import Depends, Form, Query
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from src import models,schemas
from src.database import get_db
from sqlalchemy.orm import Session

class PaginationParams(BaseModel):
     name :Optional[str]=""
     page:int=0
     limit:int=0

class AppointmentFilter(PaginationParams):
     patient_id: str | None=None
     dateFrom: str | None = None
     dateTo: str | None = None


class InProgressSessionFilter(BaseModel):
     patient_id:str | None=None
     office_id:str | None=None
     
class SessionFilter(PaginationParams):
     patient_id:str | None=None
     appointment_id:str | None=None
     date: Optional[str] = None
     
class OperationFilter(PaginationParams):
     office_id:str 
class PathologyFilter(PaginationParams):
     pass
     

dbDep = Annotated[Session, Depends(get_db)]
formDataDep = Annotated[OAuth2PasswordRequestForm, Depends()]
appointment_filter = Annotated[AppointmentFilter,Depends()]
session_filter = Annotated[SessionFilter,Depends()]
inprogress_session_filter= Annotated[InProgressSessionFilter,Depends()]
operation_filter = Annotated[OperationFilter,Depends()]
pathology_filter = Annotated[PathologyFilter,Depends()]

class PaginationParams(BaseModel):
     name :Optional[str]=""
     page:int=1
     limit:int=50



pagination_params = Annotated[PaginationParams, Depends()]



