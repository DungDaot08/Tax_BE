from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.tax import router as tax_router
from app.database import Base, engine

# Khởi tạo DB
def create_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tax Information API",
    root_path="/app",
    description="API tra cứu doanh nghiệp theo mã số thuế – CRUD – Search – Cache Redis",
    version="1.0.0",
    openapi_url="/openapi.json"
)

# CORS nếu cần cho frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # sửa lại domain thực tế nếu triển khai production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn router
app.include_router(tax_router, prefix="/api/tax", tags=["Tax"])

@app.on_event("startup")
def startup_event():
    create_tables()

@app.get("/")
def root():
    return {"message": "Tax API Running!"}
