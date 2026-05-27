from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()

# SQLite fallback for environments without PostgreSQL (tests, cold starts)
_db_url = settings.database_url
if not _db_url or _db_url == "sqlite:///:memory:":
    _db_url = "sqlite:///./fallback.db"
    _kwargs = {"connect_args": {"check_same_thread": False}}
    _pool_args = {}
else:
    _kwargs = {}
    _pool_args = {"pool_pre_ping": True, "pool_size": 10, "max_overflow": 20}

engine = create_engine(_db_url, **_kwargs, **_pool_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)
