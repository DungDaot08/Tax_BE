from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
#from dotenv import load_dotenv
#import os

# Tải biến môi trường từ .env
#load_dotenv()

# Lấy URL kết nối PostgreSQL từ biến môi trường
#DATABASE_URL = "postgresql://postgres:123@localhost:5434/postgres"
DATABASE_URL = "postgresql://taxdb:Wt7PjzYa787mBNPd8fhJHzygzlYsd7qU@dpg-d4kgo824d50c73dgcrj0-a.oregon-postgres.render.com/taxdb_nk68"

# Tạo engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # tự kiểm tra connection trước khi dùng
    pool_size=10,                # số connection trong pool
    max_overflow=20              # số connection mở rộng tối đa
)

# Tạo session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base model
Base = declarative_base()


# Dependency cho FastAPI
def get_db():
    """
    Inject session vào mỗi request.
    Tự đóng session sau khi request kết thúc.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

