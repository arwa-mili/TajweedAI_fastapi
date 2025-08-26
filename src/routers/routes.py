import uuid
from fastapi import APIRouter, HTTPException, status , BackgroundTasks
from fastapi.params import Query
from src import enums, models, schemas
from src.dependencies import dbDep, pagination_params

router = APIRouter(prefix="/routes", tags=["Routes"])

error_keys = {
    
}

