from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, literal
from typing import Optional, List
from app.database import get_db
from app import models, schemas

from app.redis_client import r
import json
import hashlib

def make_cache_key(prefix: str, **kwargs):
    raw = prefix + "_" + json.dumps(kwargs, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


router = APIRouter()


# ==========================
#  CRUD
# ==========================

@router.post("/", response_model=schemas.DangKyThueSchema)
def create_tax(data: schemas.DangKyThueSchema, db: Session = Depends(get_db)):
    db_data = models.DangKyThue(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    # purge cache nếu cần
    return db_data


@router.get("/{ma_so_thue}", response_model=schemas.DangKyThueSchema)
def get_tax(ma_so_thue: str, db: Session = Depends(get_db)):
    data = db.query(models.DangKyThue).filter(models.DangKyThue.ma_so_thue == ma_so_thue).first()
    if not data:
        raise HTTPException(status_code=404, detail="Không tìm thấy MST")
    return data


@router.put("/{ma_so_thue}", response_model=schemas.DangKyThueSchema)
def update_tax(ma_so_thue: str, payload: schemas.DangKyThueSchema, db: Session = Depends(get_db)):
    data = db.query(models.DangKyThue).filter(models.DangKyThue.ma_so_thue == ma_so_thue).first()
    if not data:
        raise HTTPException(status_code=404, detail="Không tìm thấy MST")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(data, key, value)
    db.commit()
    db.refresh(data)
    # purge cache nếu cần
    return data


@router.delete("/{ma_so_thue}")
def delete_tax(ma_so_thue: str, db: Session = Depends(get_db)):
    data = db.query(models.DangKyThue).filter(models.DangKyThue.ma_so_thue == ma_so_thue).first()
    if not data:
        raise HTTPException(status_code=404, detail="Không tìm thấy MST")
    db.delete(data)
    db.commit()
    # purge cache nếu cần
    return {"message": "Đã xóa thành công"}

@router.get("/check/{ma_so_thue}", response_model=schemas.HoKhoanCheckResponse)
def check_mst(ma_so_thue: str, db: Session = Depends(get_db)):
    result = db.query(models.HoKhoan).filter(models.HoKhoan.ma_so_thue == ma_so_thue).first()

    return schemas.HoKhoanCheckResponse(
        exists = result is not None,
        ma_so_thue = ma_so_thue
    )


# ==========================
#  SEARCH API
# ==========================

# @router.get("/search", response_model=List[schemas.DangKyThueSchema])
# def search_tax(
#     name: Optional[str] = None,
#     dia_ban: Optional[str] = None,
#     nganh_nghe: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     Tìm kiếm MST:
#     - name: tên doanh nghiệp / người nộp thuế
#     - dia_ban: tỉnh/thành phố
#     - nganh_nghe: ngành nghề kinh doanh
#     - Bỏ dấu, không phân biệt hoa thường, similarity >= 0.1
#     """
#     # Tạo cache key
#     cache_key = make_cache_key(
#         "search",
#         name=name or "",
#         dia_ban=dia_ban or "",
#         nganh_nghe=nganh_nghe or "",
#     )

#     # Kiểm tra Redis
#     cached = r.get(cache_key)
#     if cached:
#         return [schemas.DangKyThueSchema.parse_raw(x) for x in json.loads(cached)]

#     query = db.query(models.DangKyThue)

#     if name:
#         # Sử dụng PostgreSQL unaccent + lower + similarity
#         query = query.filter(
#             func.similarity(
#                 func.unaccent(func.lower(models.DangKyThue.ten_nguoi_nop_thue)),
#                 func.unaccent(func.lower(name))
#             ) >= 0.1
#         ).order_by(
#             func.similarity(
#                 func.unaccent(func.lower(models.DangKyThue.ten_nguoi_nop_thue)),
#                 func.unaccent(func.lower(name))
#             ).desc()
#         )

#     if dia_ban:
#         query = query.filter(
#             func.similarity(
#                 func.unaccent(func.lower(models.DangKyThue.ten_tinh_thanh_pho)),
#                 func.unaccent(func.lower(dia_ban))
#             ) >= 0.1
#         )

#     if nganh_nghe:
#         query = query.filter(
#             func.similarity(
#                 func.unaccent(func.lower(models.DangKyThue.ten_nganh_nghe_kd_chinh)),
#                 func.unaccent(func.lower(nganh_nghe))
#             ) >= 0.1
#         )

#     records = query.limit(50).all()

#     # Cache Redis 10 phút
#     r.setex(cache_key, 600, json.dumps([x.json() for x in records]))

# #    return records


#@router.get("/autocomplete", response_model=List[str])
#def autocomplete_company(keyword: str, db: Session = Depends(get_db)):
#    cache_key = make_cache_key("autocomplete", keyword=keyword)
#    cached = r.get(cache_key)
#    if cached:
#        return json.loads(cached)

#    results = (
#        db.query(models.DangKyThue.ten_nguoi_nop_thue)
#        .filter(models.DangKyThue.ten_nguoi_nop_thue.ilike(f"%{keyword}%"))
#        .limit(10)
#        .all()
#    )

#    names = [r[0] for r in results]

#    r.setex(cache_key, 300, json.dumps(names))

#    return names


@router.get("/", response_model=schemas.PaginatedTax)
def list_tax(
    page: int = 1,
    page_size: int = 20,
    ma_tinh: Optional[str] = None,
    nganh_nghe: Optional[str] = None,
    db: Session = Depends(get_db)
):
    cache_key = make_cache_key(
        "pagination",
        page=page,
        size=page_size,
        ma_tinh=ma_tinh or "",
        nganh_nghe=nganh_nghe or "",
    )

    cached = r.get(cache_key)
    if cached:
        return schemas.PaginatedTax.parse_raw(cached)

    query = db.query(models.DangKyThue)

    if ma_tinh:
        query = query.filter(models.DangKyThue.ma_tinh_thanh_pho == ma_tinh)
    if nganh_nghe:
        query = query.filter(models.DangKyThue.ten_nganh_nghe_kd_chinh.ilike(f"%{nganh_nghe}%"))

    total = query.count()
    items = query.offset((page-1)*page_size).limit(page_size).all()

    result = schemas.PaginatedTax(
        total=total,
        page=page,
        page_size=page_size,
        items=[schemas.DangKyThueSchema.from_orm(x) for x in items]
    )


    r.setex(cache_key, 30, result.json())

    return result

@router.get("/can_bo/{ten_can_bo}", response_model=schemas.MSTByCanBoResponse)
def get_mst_by_can_bo(ten_can_bo: str, db: Session = Depends(get_db)):
    result = (
        db.query(models.DangKyThue.ma_so_thue)
        .filter(models.DangKyThue.can_bo_quan_ly == ten_can_bo)
        .all()
    )

    ma_so_thue_list = [r[0] for r in result]

    return schemas.MSTByCanBoResponse(
        can_bo_quan_ly=ten_can_bo,
        ma_so_thue=ma_so_thue_list
    )

@router.get("/can_bo", response_model=schemas.MSTByAllCanBoResponse)
def get_all_mst_by_can_bo(db: Session = Depends(get_db)):
    # Lấy danh sách tên cán bộ (distinct)
    can_bo_list = (
        db.query(models.DangKyThue.can_bo_quan_ly)
        .distinct()
        .all()
    )

    response_data = []

    for (can_bo,) in can_bo_list:
        result = (
            db.query(models.DangKyThue.ma_so_thue)
            .filter(models.DangKyThue.can_bo_quan_ly == can_bo)
            .all()
        )

        ma_so_thue_list = [r[0] for r in result]

        response_data.append(
            schemas.MSTByCanBoResponse(
                can_bo_quan_ly=can_bo,
                ma_so_thue=ma_so_thue_list
            )
        )

    return schemas.MSTByAllCanBoResponse(data=response_data)
