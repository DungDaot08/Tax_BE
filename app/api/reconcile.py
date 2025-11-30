# routers/reconcile.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from app.database import get_db
from app import models, schemas
import numpy as np

router = APIRouter()


@router.get("/doi_chieu_hdr-hdv", response_model=schemas.ReconcileResult)
def reconcile_invoice(
    mst: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    warning_limit: Optional[float] = 1_000_000_000,  # <<< Mức cảnh báo mặc định 1 tỷ
    db: Session = Depends(get_db)
):

    # --- Xử lý ngày ---
    if start_date and not end_date:
        end_date = date.today()

    if end_date and not start_date:
        start_date = date(2000, 1, 1)

    if start_date and end_date:
        date_label = f"từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
    else:
        date_label = "toàn bộ thời gian"

    # ====== HÓA ĐƠN VÀO ======
    query_vao = db.query(models.HoaDonVao).filter(
        models.HoaDonVao.ma_so_thue_nguoi_mua == mst
    )

    if start_date:
        query_vao = query_vao.filter(models.HoaDonVao.ngay_lap >= start_date)
        query_vao = query_vao.filter(models.HoaDonVao.ngay_lap <= (end_date or date.today()))

    hd_vao_list = query_vao.all()
    so_hd_vao = len(hd_vao_list)
    tong_hd_vao = sum(h.tong_tien_thanh_toan or 0 for h in hd_vao_list)

    # ====== HÓA ĐƠN RA ======
    query_ra = db.query(models.HoaDonRa).filter(
        models.HoaDonRa.ma_so_thue_nguoi_ban == mst
    )

    if start_date:
        query_ra = query_ra.filter(models.HoaDonRa.ngay_lap >= start_date)
        query_ra = query_ra.filter(models.HoaDonRa.ngay_lap <= (end_date or date.today()))

    hd_ra_list = query_ra.all()
    so_hd_ra = len(hd_ra_list)
    tong_hd_ra = sum(h.tong_tien_thanh_toan or 0 for h in hd_ra_list)

    # ====== CHÊNH LỆCH ======
    chenhlech = tong_hd_ra - tong_hd_vao

    # ====== CẢNH BÁO ======
    if abs(chenhlech) >= warning_limit:
        canh_bao = "NGUY HIỂM – Chênh lệch vượt mức cảnh báo!"
    else:
        canh_bao = "Bình thường"

    return schemas.ReconcileResult(
        ma_so_thue=mst,
        so_hd_vao=so_hd_vao,
        so_hd_ra=so_hd_ra,
        tong_hd_vao=tong_hd_vao,
        tong_hd_ra=tong_hd_ra,
        chenhlech=chenhlech,
        khoang_thoi_gian=date_label,
        canh_bao=canh_bao,
        hoa_don_vao=hd_vao_list,
        hoa_don_ra=hd_ra_list
    )

from fastapi import APIRouter, UploadFile, File, Form
import pandas as pd
from typing import Optional
from datetime import datetime
from io import BytesIO

# @router.post("/doichieu-hdr-doanhthu")
# async def compare_invoice_revenue(
#     file_invoices: UploadFile = File(...),
#     file_hkd: UploadFile = File(...),
#     mst_list: str = Form(...),
#     start_date: Optional[str] = Form(None),
#     end_date: Optional[str] = Form(None),
#     warning_level: Optional[float] = Form(1_000_000_000)
# ):
#     # ------------------------
#     # 1️⃣ MST list
#     # ------------------------
#     msts = [x.strip() for x in mst_list.split(";")]

#     # ------------------------
#     # 2️⃣ Chỉ đọc sheet đầu tiên
#     # ------------------------
#     file_invoices.file.seek(0)
#     df_invoice = pd.read_excel(BytesIO(file_invoices.file.read()), sheet_name=0, engine="openpyxl")

#     file_hkd.file.seek(0)
#     df_hkd = pd.read_excel(BytesIO(file_hkd.file.read()), sheet_name=0, engine="openpyxl")

#     # ------------------------
#     # 3️⃣ Chuẩn hóa cột
#     # ------------------------
#     df_invoice.columns = df_invoice.columns.str.strip().str.lower()
#     df_hkd.columns = df_hkd.columns.str.strip().str.lower()

#     COL_MST_HKD = "mst"
#     COL_DT_KK = "doanh thu trên tờ khai"

#     COL_MST_HD = "mst người mua/mst người nhận hàng"
#     COL_TOTAL = "tổng tiền thanh toán"
#     COL_NGAY = "ngày lập"
#     COL_SOHD = "số hóa đơn"
#     COL_KYHIEU = "ký hiệu"

#     # Chuẩn hóa MST
#     df_hkd[COL_MST_HKD] = df_hkd[COL_MST_HKD].astype(str).str.replace(r"[.,]", "", regex=True).str.strip()
#     df_invoice[COL_MST_HD] = df_invoice[COL_MST_HD].astype(str).str.replace(r"[.,]", "", regex=True).str.strip()

#     # Chuẩn hóa số tiền
#     df_hkd[COL_DT_KK] = pd.to_numeric(df_hkd[COL_DT_KK], errors="coerce").fillna(0)
#     df_invoice[COL_TOTAL] = pd.to_numeric(df_invoice[COL_TOTAL], errors="coerce").fillna(0)

#     # ------------------------
#     # 4️⃣ Chuyển ngày: nhận dạng mọi dạng DD/MM/YYYY, D/M/YYYY, Excel serial
#     # ------------------------
#     if COL_NGAY in df_invoice.columns:
#         def parse_excel_date(x):
#             if pd.isna(x):
#                 return pd.NaT
#             # Excel serial number
#             if isinstance(x, (int, float, np.number)):
#                 try:
#                     return pd.to_datetime(x, origin='1899-12-30', unit='D')
#                 except:
#                     return pd.NaT
#             # Text
#             try:
#                 return pd.to_datetime(str(x), dayfirst=True, errors='coerce')
#             except:
#                 return pd.NaT

#         df_invoice[COL_NGAY] = df_invoice[COL_NGAY].apply(parse_excel_date)

#     # ------------------------
#     # 5️⃣ Lọc theo ngày
#     # ------------------------
#     if start_date:
#         start_dt = pd.to_datetime(start_date, dayfirst=True, errors="coerce")
#         df_invoice = df_invoice[df_invoice[COL_NGAY] >= start_dt]
#     if end_date:
#         end_dt = pd.to_datetime(end_date, dayfirst=True, errors="coerce")
#         df_invoice = df_invoice[df_invoice[COL_NGAY] <= end_dt]

#     # ------------------------
#     # 6️⃣ Tính toán đối chiếu & Pivot Table chi tiết
#     # ------------------------
#     results = []
#     for mst in msts:
#         mst_clean = mst.replace(".", "").replace(",", "").strip()

#         # Doanh thu kê khai
#         df_h = df_hkd[df_hkd[COL_MST_HKD] == mst_clean]
#         dt_kekhai = float(df_h[COL_DT_KK].sum()) if not df_h.empty else 0

#         # HĐRA chi tiết
#         df_inv = df_invoice[df_invoice[COL_MST_HD] == mst_clean]
#         tong_hdr = float(df_inv[COL_TOTAL].sum()) if not df_inv.empty else 0

#         # Chênh lệch & cảnh báo
#         chenhlech = tong_hdr - dt_kekhai
#         if chenhlech >= warning_level:
#             canh_bao = f"🚨 MỨC BÁO ĐỘNG: Chênh lệch ≥ {warning_level:,} đồng"
#         elif tong_hdr > dt_kekhai:
#             canh_bao = "⚠️ Nguy cơ che giấu doanh thu (HĐR > Doanh thu kê khai)"
#         else:
#             canh_bao = "Bình thường"

#         # Chi tiết hóa đơn (Pivot Table style)
#         chi_tiet_hd = []
#         if not df_inv.empty:
#             for _, row in df_inv.iterrows():
#                 chi_tiet_hd.append({
#                     "so_hoa_don": row.get(COL_SOHD, ""),
#                     "ky_hieu": row.get(COL_KYHIEU, ""),
#                     "ngay_lap": row.get(COL_NGAY, pd.NaT).strftime("%Y-%m-%d") if pd.notnull(row.get(COL_NGAY)) else "",
#                     "tong_tien": row.get(COL_TOTAL, 0)
#                 })

#         results.append({
#             "mst": mst_clean,
#             "doanh_thu_hoa_don_ra": tong_hdr,
#             "doanh_thu_khai_bao": dt_kekhai,
#             "chenh_lech": chenhlech,
#             "muc_canh_bao": warning_level,
#             "ket_luan": canh_bao,
#             "so_hoa_don_duoc_tinh": len(df_inv),
#             "chi_tiet_hoa_don": chi_tiet_hd
#         })

#     return {
#         "so_mst_kiem_tra": len(msts),
#         "tu_ngay": start_date,
#         "den_ngay": end_date,
#         "muc_canh_bao": warning_level,
#         "ket_qua": results
#     }

@router.get("/doi_chieu_hdv-doanhthu", response_model=schemas.ReconcileResult_HDV_Doanh_thu)
def reconcile_invoice(
    mst: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    #warning_limit: Optional[float] = 1_000_000_000,  # <<< Mức cảnh báo mặc định 1 tỷ
    db: Session = Depends(get_db)
):

    # --- Xử lý ngày ---
    if start_date and not end_date:
        end_date = date.today()

    if end_date and not start_date:
        start_date = date(2000, 1, 1)

    if start_date and end_date:
        date_label = f"từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
    else:
        date_label = "toàn bộ thời gian"

    # ====== HÓA ĐƠN VÀO ======
    query_vao = db.query(models.HoaDonVao).filter(
        models.HoaDonVao.ma_so_thue_nguoi_mua == mst
    )

    if start_date:
        query_vao = query_vao.filter(models.HoaDonVao.ngay_lap >= start_date)
        query_vao = query_vao.filter(models.HoaDonVao.ngay_lap <= (end_date or date.today()))

    hd_vao_list = query_vao.all()
    so_hd_vao = len(hd_vao_list)
    tong_hd_vao = sum(h.tong_tien_thanh_toan or 0 for h in hd_vao_list)

    # ====== HÓA ĐƠN RA ======
    query_doanh_thu = db.query(models.DangKyThue).filter(
        models.DangKyThue.ma_so_thue == mst
    ).first()
    doanh_thu_ke_khai = query_doanh_thu.doanh_thu_ke_khai if query_doanh_thu and query_doanh_thu.doanh_thu_ke_khai else 0

    # ====== CHÊNH LỆCH ======
    chenhlech = doanh_thu_ke_khai - tong_hd_vao

    # ====== CẢNH BÁO ======
    if chenhlech < 0:
        canh_bao = "HĐV lớn hơn Doanh thu"
    else:
        canh_bao = "Bình thường"

    return schemas.ReconcileResult_HDV_Doanh_thu(
        ma_so_thue=mst,
        so_hd_vao=so_hd_vao,
        tong_hd_vao=tong_hd_vao,
        doanh_thu_ke_khai=doanh_thu_ke_khai,
        chenhlech=chenhlech,
        khoang_thoi_gian=date_label,
        canh_bao=canh_bao,
        hoa_don_vao=hd_vao_list
    )
    
@router.get("/doi_chieu_hdr-doanhthu", response_model=schemas.ReconcileResult_HDR_Doanh_thu)
def reconcile_invoice(
    mst: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    #warning_limit: Optional[float] = 1_000_000_000,  # <<< Mức cảnh báo mặc định 1 tỷ
    db: Session = Depends(get_db)
):

    # --- Xử lý ngày ---
    if start_date and not end_date:
        end_date = date.today()

    if end_date and not start_date:
        start_date = date(2000, 1, 1)

    if start_date and end_date:
        date_label = f"từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
    else:
        date_label = "toàn bộ thời gian"

    # ====== HÓA ĐƠN VÀO ======
    query_vao = db.query(models.HoaDonRa).filter(
        models.HoaDonRa.ma_so_thue_nguoi_mua == mst
    )

    if start_date:
        query_vao = query_vao.filter(models.HoaDonRa.ngay_lap >= start_date)
        query_vao = query_vao.filter(models.HoaDonRa.ngay_lap <= (end_date or date.today()))

    hd_ra_list = query_vao.all()
    so_hd_ra = len(hd_ra_list)
    tong_hd_ra = sum(h.tong_tien_thanh_toan or 0 for h in hd_ra_list)

    # ====== HÓA ĐƠN RA ======
    query_doanh_thu = db.query(models.DangKyThue).filter(
        models.DangKyThue.ma_so_thue == mst
    ).first()
    doanh_thu_ke_khai = query_doanh_thu.doanh_thu_ke_khai if query_doanh_thu and query_doanh_thu.doanh_thu_ke_khai else 0

    # ====== CHÊNH LỆCH ======
    chenhlech = doanh_thu_ke_khai - tong_hd_ra

    # ====== CẢNH BÁO ======
    if chenhlech < 0:
        canh_bao = "HĐR lớn hơn Doanh thu"
    else:
        canh_bao = "Bình thường"

    return schemas.ReconcileResult_HDR_Doanh_thu(
        ma_so_thue=mst,
        so_hd_ra=so_hd_ra,
        tong_hd_ra=tong_hd_ra,
        doanh_thu_ke_khai=doanh_thu_ke_khai,
        chenhlech=chenhlech,
        khoang_thoi_gian=date_label,
        canh_bao=canh_bao,
        hoa_don_ra=hd_ra_list
    )