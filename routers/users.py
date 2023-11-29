import sys
sys.path.append("..")

from fastapi import APIRouter, Depends, Path, Query, HTTPException
import db.models
from db.database import engine, SessionLocal
from starlette import status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from .auth import get_current_user, user_not_found_exception, authenticate_user, create_access_token, verify_password, get_password_hash, bad_request, empty_task_response
#from .tasks import get_pages_amount, get_sub_set_by_page_no
from datetime import timedelta #auth
from fastapi.security import OAuth2PasswordRequestForm #auth

router = APIRouter(
	prefix="/users",
	tags=["users"],
	responses={404:{"description":"Not Found"},
	401:{"description":"Not Authenticated"}}
	)

db.models.Base.metadata.create_all(bind=engine)

def get_db():
	try:
		db_session = SessionLocal()
		yield db_session
	finally:
		db_session.close()

def success_response(code:int):
	return {
		'status': code,
		'transaction': "successful"
	}

class EditUser(BaseModel):
	email: Optional[str]
	password: str

	class Config:
		schema_extra = {
			'example': {
				'email': 'test@gmail.com',
				'password': 'test'
			}
		}

@router.get("/all")
async def get_all_users(user: dict = Depends(get_current_user), db_session: Session = Depends(get_db)):
	return db_session.query(db.models.User).order_by(db.models.User.id).all()

@router.get("/all/{page_no}")
async def get_all_users(page_no: int, query_email: str = "", query_username: str = "", user: dict = Depends(get_current_user), db_session: Session = Depends(get_db)):
	the_user_models = db_session.query(db.models.User).order_by(db.models.User.id).filter(db.models.User.email.like(f'%{query_email}%')).filter(db.models.User.username.like(f'%{query_username}%')).all()
	amount_of_pages = get_pages_amount(the_user_models)
	sub_set_of_the_user_models = get_sub_set_by_page_no(the_user_models, page_no)
	return {
		'pages': amount_of_pages,
		'list': sub_set_of_the_user_models
	}
