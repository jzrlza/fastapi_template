from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

config = {
    "test": True,
    "postgre_connection": "postgresql://postgres:1234@localhost:5432/testdb",
    "postgre_connection_real": "real_db_url",
  }

if config["test"] :
    print("using postgres local")
    SQLALCHEMY_DATABASE_URL = config["postgre_connection"]
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    """
    print("using sqlite")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./mock.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    """
else :
    print("using postgres real")
    SQLALCHEMY_DATABASE_URL = config["postgre_connection_real"]
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()