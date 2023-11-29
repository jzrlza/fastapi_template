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
		db = SessionLocal()
		yield db
	finally:
		db.close()

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
async def get_all_users(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	return db.query(database.models.User).order_by(database.models.User.id).all()

@router.get("/all/{page_no}")
async def get_all_users(page_no: int, query_email: str = "", query_username: str = "", user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	the_user_models = db.query(database.models.User).order_by(database.models.User.id).filter(database.models.User.email.like(f'%{query_email}%')).filter(database.models.User.username.like(f'%{query_username}%')).all()
	amount_of_pages = get_pages_amount(the_user_models)
	sub_set_of_the_user_models = get_sub_set_by_page_no(the_user_models, page_no)
	return {
		'pages': amount_of_pages,
		'list': sub_set_of_the_user_models
	}

"""
@router.get("/info")
async def read_self_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	return db.query(database.models.User).filter(database.models.User.id == user.get("id")).first()

@router.get("/info/{user_id}")
async def read_other_user(user_id:int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	return db.query(database.models.User).filter(database.models.User.id == user_id).first()

@router.get("/info-minimal")
async def read_self_user_without_password(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	the_user_model = db.query(database.models.User).filter(database.models.User.id == user.get("id")).first()

	recent_task = None
	recent_task_record = None
	if the_user_model.recent_task_id is not None:
		recent_task = db.query(database.models.Task).filter(database.models.Task.id == the_user_model.recent_task_id).filter(database.models.Task.is_deleted == False).first()
		if recent_task is None :
			raise empty_task_response()
		recent_task_record = db.query(database.models.TaskRecord).filter(database.models.TaskRecord.task_id == the_user_model.recent_task_id).filter(database.models.TaskRecord.owner_id == user.get("id")).filter(database.models.TaskRecord.is_deleted == False).first()
		if recent_task_record is None :
			raise empty_task_response()
		the_sub_task_models = db.query(database.models.SubTask).filter(database.models.SubTask.task_id == recent_task.id).filter(database.models.SubTask.is_deleted == False).order_by(database.models.SubTask.id).all()
		if the_sub_task_models is None or len(the_sub_task_models) == 0 :
			raise empty_task_response()
		setattr(recent_task, "sub_tasks_amount", len(the_sub_task_models))

	return {
		'id': the_user_model.id,
		'email': the_user_model.email,
		'username': the_user_model.username,
		'is_admin': the_user_model.is_admin,
		'recent_task': recent_task,
		'recent_task_record': recent_task_record
	}

@router.put("/info")
async def edit_self_user(edit_user:EditUser, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	user = db.query(database.models.User).filter(database.models.User.id == user.get("id")).first()
	if not user:
		raise user_not_found_exception()

	user.email=edit_user.email
	#user.username = create_user.username
	user.hashed_password = get_password_hash(edit_user.password)

	db.add(user)
	db.commit()
	return success_response(200)

@router.put("/edit/{user_id}")
async def edit_other_user(user_id:int, edit_user:EditUser, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	other_user = db.query(database.models.User).filter(database.models.User.id == user_id).first()
	if not other_user:
		raise user_not_found_exception()

	if user.get("is_admin") == False :
		raise user_not_found_exception()

	other_user.email=edit_user.email
	#user.username = create_user.username
	other_user.hashed_password = get_password_hash(edit_user.password)

	db.add(other_user)
	db.commit()
	return success_response(200)

@router.delete("/info")
async def suspend_self_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	user = db.query(database.models.User).filter(database.models.User.id == user_id).first()
	if not user:
		raise user_not_found_exception()

	user.is_active = False

	db.add(user)
	db.commit()

	return success_response(201)

@router.delete("/info/bye")
async def remove_self_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	user = db.query(database.models.User).filter(database.models.User.id == user.get("id")).first()
	if not user:
		raise user_not_found_exception()

	db.query(database.models.TaskRecord).filter(database.models.TaskRecord.owner_id == user.get("id")).delete()
	db.query(database.models.Answer).filter(database.models.Answer.user_id == user.get("id")).delete()
	db.query(database.models.User).filter(database.models.User.id == user.get("id")).delete()
	db.commit()

	return success_response(201)

@router.delete("/remove/{user_id}")
async def suspend_other_user(user_id:int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	other_user = db.query(database.models.User).filter(database.models.User.id == user_id).first()
	if not other_user:
		raise user_not_found_exception()

	if user.get("is_admin") == False :
		raise user_not_found_exception()

	other_user.is_active = False

	db.add(other_user)
	db.commit()
	return success_response(201)

@router.put("/unremove/{user_id}")
async def unsuspend_other_user(user_id:int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	other_user = db.query(database.models.User).filter(database.models.User.id == user_id).first()
	if not other_user:
		raise user_not_found_exception()

	if user.get("is_admin") == False :
		raise user_not_found_exception()

	other_user.is_active = True

	db.add(other_user)
	db.commit()
	return success_response(201)

@router.delete("/remove/{user_id}/terminate")
async def remove_other_user(user_id:int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
	other_user = db.query(database.models.User).filter(database.models.User.id == user_id).first()
	if not other_user:
		raise user_not_found_exception()

	if user.get("is_admin") == False :
		raise user_not_found_exception()

	db.query(database.models.TaskRecord).filter(database.models.TaskRecord.owner_id == user_id).delete()
	db.query(database.models.Answer).filter(database.models.Answer.user_id == user_id).delete()
	db.query(database.models.User).filter(database.models.User.id == user_id).delete()
	db.commit()

	return success_response(201)
"""