import sys
sys.path.append("..")
import random

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import db.models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

#import config

config = {
    "test": False,
    "data_path": "./data",
    "allow_origins": [],
    "storage": 
            {
                "type": "filesystem",
                "path": "pgdata"
            },
  }

SECRET_KEY = "MOCK" #random string, anything
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60
REFRESH_TOKEN_EXPIRE_MINUTES = 24 * 60 * 5
#ADMIN_PASSWORD_PROOF = config.get_config("admin_access_proof")

class CreateUser(BaseModel):
	username: str = Field(min_length=4)
	email: str = Field(min_length=4)
	password: str = Field(min_length=4, description="security")
	confirm_password: Optional[str]

	class Config:
		schema_extra = {
			'example': {
				'username': 'test',
				'email': 'test@email.com',
				'password': 'test',
				'confirm_password': 'test'
			}
		}

class CreateAdmin(BaseModel):
	username: str = Field(min_length=4)
	email: str = Field(min_length=4)
	password: str = Field(min_length=4, description="security")
	admin_verify_password: str

	class Config:
		schema_extra = {
			'example': {
				'username': 'test',
				'email': 'test@email.com',
				'password': 'test',
				'admin_verify_password': 'some_access_proof'
			}
		}

bcrypt_context = CryptContext(schemes=["bcrypt"])

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
	prefix="/auth",
	tags=["auth"],
	responses={401:{"user":"Not Auth"}}
	)

db.models.Base.metadata.create_all(bind=engine)

def get_db():
	try:
		db = SessionLocal()
		yield db
	finally:
		db.close()

def get_password_hash(password):
	return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
	return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(email:str, password:str, db):
	user = db.query(database.models.User).filter(database.models.User.email == email).first()

	if not user:
		return False
	if not verify_password(password, user.hashed_password):
		return False

	return user

def create_access_token(email:str, user_id:int, expires_delta:Optional[timedelta] = None, is_admin:bool = False):
	encode = {
		"email": email,
		"id": user_id,
		"is_admin": is_admin
	}
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(minutes=15)
	encode.update({"exp": expire})
	return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def success_response(code:int):
	return {
		'status': code,
		'transaction': "successful"
	}

def user_not_found_exception():
	return HTTPException(status_code=401, detail="ไม่พบผู้ใช้งานที่ตรงกับรหัสผ่านที่ถูกต้อง",
		headers={"WWW-Authenticate": "Bearer"})

def empty_task_response():
	return HTTPException(status_code=501, detail="task is empty",
		headers={"WWW-Authenticate": "Bearer"})

def bad_request(reason:str):
	return HTTPException(status_code=400, detail=reason,
		headers={"WWW-Authenticate": "Bearer"})

async def get_current_user(token:str = Depends(oauth2_bearer)):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("email")
		user_id: int = payload.get("id")
		is_admin: bool = payload.get("is_admin")
		if username is None or user_id is None:
			raise user_not_found_exception()
		return {
			"username": username,
			"id": user_id,
			"is_admin": is_admin
		}
	except JWTError:
		raise user_not_found_exception()

@router.post("/create/user")
async def registration(create_user:CreateUser, db: Session = Depends(get_db)):
	if create_user.email == "" :
		raise bad_request("อีเมลว่างเปล่า")

	if create_user.username == "" :
		raise bad_request("ชื่อผู้ใช้ว่างเปล่า")

	if create_user.password == "" :
		raise bad_request("รหัสผ่านว่างเปล่า")

	if create_user.confirm_password != create_user.password :
		raise bad_request("ยืนยันรหัสผ่านไม่ถูกต้อง (ต้องเหมือนกัน)")

	email_already = db.query(database.models.User).filter(database.models.User.email == create_user.email).first()
	if email_already is not None :
		raise bad_request("อีเมลนี้ถูกใช้งานแล้ว")
	username_already = db.query(database.models.User).filter(database.models.User.username == create_user.username).first()
	if username_already is not None :
		raise bad_request("ชื่อผู้ใช้นี้ถูกใช้งานแล้ว")

	create_user_model = database.models.User()
	create_user_model.email = create_user.email
	create_user_model.username = create_user.username
	create_user_model.hashed_password = get_password_hash(create_user.password)
	create_user_model.is_active = True
	create_user_model.is_admin = False
	db.add(create_user_model)
	db.commit()

	return success_response(200)

@router.post("/create/admin")
async def registration_for_admin(create_user:CreateAdmin, db: Session = Depends(get_db)):
	if create_user.email == "" :
		raise bad_request("อีเมลว่างเปล่า")

	if create_user.username == "" :
		raise bad_request("ชื่อผู้ใช้ว่างเปล่า")

	if create_user.password == "" :
		raise bad_request("รหัสผ่านว่างเปล่า")

	#if create_user.admin_verify_password != ADMIN_PASSWORD_PROOF :
	#	raise bad_request("รหัสเฉพาะ Admin ไม่ถูกต้อง")

	email_already = db.query(database.models.User).filter(database.models.User.email == create_user.email).first()
	if email_already is not None :
		raise bad_request("อีเมลนี้ถูกใช้งานแล้ว")
	username_already = db.query(database.models.User).filter(database.models.User.username == create_user.username).first()
	if username_already is not None :
		raise bad_request("ชื่อผู้ใช้นี้ถูกใช้งานแล้ว")

	create_user_model = database.models.User()
	create_user_model.email = create_user.email
	create_user_model.username = create_user.username
	create_user_model.hashed_password = get_password_hash(create_user.password)
	create_user_model.is_active = True
	create_user_model.is_admin = True
	db.add(create_user_model)
	db.commit()
	return success_response(200)

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
	if form_data.username == "" :
		raise bad_request("อีเมลว่างเปล่า")

	if form_data.password == "" :
		raise bad_request("รหัสผ่านว่างเปล่า")

	user = authenticate_user(form_data.username, form_data.password, db)

	if not user:
		raise user_not_found_exception()

	if not user.is_active :
		raise bad_request("ผู้ใช้งานถูกระงับการใช้งาน")

	token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	token = create_access_token(user.email, user.id, expires_delta=token_expires, is_admin=user.is_admin)

	return {"token": token}