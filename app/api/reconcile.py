# routers/reconcile.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from app.database import get_db
from app import models, schemas
import numpy as np

router = APIRouter()


# @router.get("/doi_chieu_hdr-hdv", response_model=schemas.ReconcileResult)
# def reconcile_invoice(
#     mst: str,
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
#     warning_limit: Optional[float] = 1_000_000_000,  # <<< Mức cảnh báo mặc định 1 tỷ
#     db: Session = Depends(get_db)
# ):

#     # --- Xử lý ngày ---
#     if start_date and not end_date:
#         end_date = date.today()

#     if end_date and not start_date:
#         start_date = date(2000, 1, 1)

#     if start_date and end_date:
#         date_label = f"từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
#     else:
#         date_label = "toàn bộ thời gian"

#     # ====== HÓA ĐƠN VÀO ======
#     query_vao = db.query(models.HoaDonVao).filter(
#         models.HoaDonVao.ma_so_thue_nguoi_mua == mst
#     )

#     if start_date:
#         query_vao = query_vao.filter(models.HoaDonVao.ngay_lap >= start_date)
#         query_vao = query_vao.filter(models.HoaDonVao.ngay_lap <= (end_date or date.today()))

#     hd_vao_list = query_vao.all()
#     so_hd_vao = len(hd_vao_list)
#     tong_hd_vao = sum(h.tong_tien_thanh_toan or 0 for h in hd_vao_list)

#     # ====== HÓA ĐƠN RA ======
#     query_ra = db.query(models.HoaDonRa).filter(
#         models.HoaDonRa.ma_so_thue_nguoi_ban == mst
#     )

#     if start_date:
#         query_ra = query_ra.filter(models.HoaDonRa.ngay_lap >= start_date)
#         query_ra = query_ra.filter(models.HoaDonRa.ngay_lap <= (end_date or date.today()))

#     hd_ra_list = query_ra.all()
#     so_hd_ra = len(hd_ra_list)
#     tong_hd_ra = sum(h.tong_tien_thanh_toan or 0 for h in hd_ra_list)

#     # ====== CHÊNH LỆCH ======
#     chenhlech = tong_hd_ra - tong_hd_vao

#     # ====== CẢNH BÁO ======
#     if abs(chenhlech) >= warning_limit:
#         canh_bao = "NGUY HIỂM – Chênh lệch vượt mức cảnh báo!"
#     else:
#         canh_bao = "Bình thường"

#     return schemas.ReconcileResult(
#         ma_so_thue=mst,
#         so_hd_vao=so_hd_vao,
#         so_hd_ra=so_hd_ra,
#         tong_hd_vao=tong_hd_vao,
#         tong_hd_ra=tong_hd_ra,
#         chenhlech=chenhlech,
#         khoang_thoi_gian=date_label,
#         canh_bao=canh_bao,
#         #hoa_don_vao=hd_vao_list,
#         #hoa_don_ra=hd_ra_list
#         hoa_don_vao=[schemas.HoaDonVaoSchema.from_orm(h) for h in hd_vao_list],
#         hoa_don_ra=[schemas.HoaDonRaSchema.from_orm(h) for h in hd_ra_list]
#     )

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
    db: Session = Depends(get_db)
):

    # ============================
    # XỬ LÝ NGÀY
    # ============================

    # Nếu chỉ có start → end = hôm nay
    if start_date and not end_date:
        end_date = date.today()

    # Nếu chỉ có end → start = mốc rộng
    if end_date and not start_date:
        start_date = date(2000, 1, 1)

    # Tính nhãn ngày
    if start_date and end_date:
        date_label = f"từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
    else:
        date_label = "toàn bộ thời gian"


    # ============================
    # TÍNH SỐ THÁNG TRONG KHOẢNG THỜI GIAN
    # ============================

    if start_date and end_date:
        # Số tháng = (năm * 12 + tháng)
        total_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
    else:
        total_months = 1   # không chọn ngày → coi như 1 tháng để tránh lỗi


    # ============================
    # LẤY HÓA ĐƠN VÀO
    # ============================

    query_vao = db.query(models.HoaDonVao).filter(
        models.HoaDonVao.ma_so_thue_nguoi_mua == mst
    )

    if start_date:
        query_vao = query_vao.filter(models.HoaDonVao.ngay_lap >= start_date)
        query_vao = query_vao.filter(models.HoaDonVao.ngay_lap <= end_date)

    hd_vao_list = query_vao.all()
    so_hd_vao = len(hd_vao_list)
    tong_hd_vao = sum((h.tong_tien_thanh_toan or 0) for h in hd_vao_list)


    # ============================
    # LẤY DOANH THU TỪ BẢNG HỘ KHOÁN
    # ============================

    ho_khoan = db.query(models.HoKhoan).filter(
        models.HoKhoan.ma_so_thue == mst
    ).first()

    if ho_khoan:
        doanh_thu_1_thang = float(ho_khoan.doanh_thu or 0)
    else:
        doanh_thu_1_thang = 0


    # Doanh thu * số tháng trong khoảng thời gian
    doanh_thu_ky = doanh_thu_1_thang * total_months


    # ============================
    # CHÊNH LỆCH
    # ============================

    chenhlech = doanh_thu_ky - tong_hd_vao


    # ============================
    # CẢNH BÁO
    # ============================

    if chenhlech < 0:
        canh_bao = "HĐV lớn hơn Doanh thu kỳ"
    else:
        canh_bao = "Bình thường"


    # ============================
    # TRẢ KẾT QUẢ
    # ============================

    return schemas.ReconcileResult_HDV_Doanh_thu(
        ma_so_thue=mst,
        so_hd_vao=so_hd_vao,
        tong_hd_vao=tong_hd_vao,
        doanh_thu_ke_khai=doanh_thu_ky,
        chenhlech=chenhlech,
        khoang_thoi_gian=date_label,
        so_thang=total_months,
        canh_bao=canh_bao,
        hoa_don_vao=[schemas.HoaDonVaoSchema.from_orm(h) for h in hd_vao_list]
    )

    
@router.get("/doi_chieu_hdr-doanhthu", response_model=schemas.ReconcileResult_HDR_Doanh_thu)
def reconcile_invoice_out(
    mst: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):

    # ============================
    # XỬ LÝ NGÀY
    # ============================
    if start_date and not end_date:
        end_date = date.today()

    if end_date and not start_date:
        start_date = date(2000, 1, 1)

    if start_date and end_date:
        date_label = f"từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
    else:
        date_label = "toàn bộ thời gian"


    # ============================
    # TÍNH SỐ THÁNG
    # ============================
    if start_date and end_date:
        total_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
    else:
        total_months = 1


    # ============================
    # LẤY HÓA ĐƠN RA
    # ============================

    query_ra = db.query(models.HoaDonRa).filter(
        models.HoaDonRa.ma_so_thue_nguoi_ban == mst
    )

    if start_date:
        query_ra = query_ra.filter(models.HoaDonRa.ngay_lap >= start_date)
        query_ra = query_ra.filter(models.HoaDonRa.ngay_lap <= end_date)

    hd_ra_list = query_ra.all()
    so_hd_ra = len(hd_ra_list)
    tong_hd_ra = sum((h.tong_tien_thanh_toan or 0) for h in hd_ra_list)


    # ============================
    # LẤY DOANH THU 1 THÁNG TỪ HỘ KHOÁN
    # ============================

    ho_khoan = db.query(models.HoKhoan).filter(
        models.HoKhoan.ma_so_thue == mst
    ).first()

    doanh_thu_1_thang = float(ho_khoan.doanh_thu or 0) if ho_khoan else 0

    # Doanh thu kỳ = doanh thu 1 tháng * số tháng
    doanh_thu_ky = doanh_thu_1_thang * total_months


    # ============================
    # CHÊNH LỆCH
    # ============================
    chenhlech = doanh_thu_ky - tong_hd_ra


    # ============================
    # CẢNH BÁO
    # ============================
    if chenhlech < 0:
        canh_bao = "HĐR lớn hơn Doanh thu kỳ"
    else:
        canh_bao = "Bình thường"


    # ============================
    # TRẢ KẾT QUẢ
    # ============================

    return schemas.ReconcileResult_HDR_Doanh_thu(
        ma_so_thue=mst,
        so_hd_ra=so_hd_ra,
        tong_hd_ra=tong_hd_ra,
        doanh_thu_ky=doanh_thu_ky,
        chenhlech=chenhlech,
        so_thang=total_months,
        khoang_thoi_gian=date_label,
        canh_bao=canh_bao,
        hoa_don_ra=[schemas.HoaDonRaSchema.from_orm(h) for h in hd_ra_list]
    )

    
@router.get("/doi_chieu_hdr-hdv", response_model=schemas.ReconcileResult)
def reconcile_invoice(
    mst: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    warning_limit: Optional[float] = 1_000_000_000,
    db: Session = Depends(get_db)
):

    # =========================
    # XỬ LÝ NGÀY
    # =========================
    if start_date and not end_date:
        end_date = date.today()

    if end_date and not start_date:
        start_date = date(2000, 1, 1)

    if not start_date and not end_date:
        start_date = date(2000, 1, 1)
        end_date = date.today()

    date_label = f"từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"

    # ====================================================
    # HÓA ĐƠN VÀO – NĂM NAY
    # ====================================================
    hd_vao_list = db.query(models.HoaDonVao).filter(
        models.HoaDonVao.ma_so_thue_nguoi_mua == mst,
        models.HoaDonVao.ngay_lap >= start_date,
        models.HoaDonVao.ngay_lap <= end_date
    ).all()

    so_hd_vao = len(hd_vao_list)
    tong_hd_vao = sum(h.tong_tien_thanh_toan or 0 for h in hd_vao_list)

    # ====================================================
    # HÓA ĐƠN RA – NĂM NAY
    # ====================================================
    hd_ra_list = db.query(models.HoaDonRa).filter(
        models.HoaDonRa.ma_so_thue_nguoi_ban == mst,
        models.HoaDonRa.ngay_lap >= start_date,
        models.HoaDonRa.ngay_lap <= end_date
    ).all()

    so_hd_ra = len(hd_ra_list)
    tong_hd_ra = sum(h.tong_tien_thanh_toan or 0 for h in hd_ra_list)

    # =========================
    # CHÊNH LỆCH
    # =========================
    chenhlech = (tong_hd_ra or 0) - (tong_hd_vao or 0)
    canh_bao = (
        "NGUY HIỂM – Chênh lệch vượt mức cảnh báo!"
        if abs(chenhlech) >= warning_limit else
        "Bình thường"
    )

    # =========================
    # TRẢ VỀ DỮ LIỆU
    # =========================
    return schemas.ReconcileResult(
        ma_so_thue=mst,
        khoang_thoi_gian=date_label,

        so_hd_vao=so_hd_vao,
        so_hd_ra=so_hd_ra,
        tong_hd_vao=tong_hd_vao,
        tong_hd_ra=tong_hd_ra,

        chenhlech=chenhlech,
        canh_bao=canh_bao,

        hoa_don_vao=[schemas.HoaDonVaoSchema.from_orm(h) for h in hd_vao_list],
        hoa_don_ra=[schemas.HoaDonRaSchema.from_orm(h) for h in hd_ra_list],
    )



@router.get("/doi_chieu_hdr_cung_ky", response_model=schemas.ReconcileHDR)
def reconcile_invoice_ra(
    mst: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    warning_limit: Optional[float] = 1_000_000_000,
    db: Session = Depends(get_db)
):

    # =========================
    # XỬ LÝ NGÀY
    # =========================
    if start_date and not end_date:
        end_date = date.today()

    if end_date and not start_date:
        start_date = date(2000, 1, 1)

    if not start_date and not end_date:
        start_date = date(2000, 1, 1)
        end_date = date.today()

    # Nhãn khoảng thời gian
    date_label = f"từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"

    # --- Khoảng thời gian cùng kỳ năm trước ---
    prev_start = date(start_date.year - 1, start_date.month, start_date.day)
    prev_end = date(end_date.year - 1, end_date.month, end_date.day)

    # ====================================================
    # HÓA ĐƠN RA – NĂM NAY
    # ====================================================
    hd_ra_list = db.query(models.HoaDonRa).filter(
        models.HoaDonRa.ma_so_thue_nguoi_ban == mst,
        models.HoaDonRa.ngay_lap >= start_date,
        models.HoaDonRa.ngay_lap <= end_date
    ).all()

    so_hd_ra = len(hd_ra_list)
    tong_hd_ra = sum(h.tong_tien_thanh_toan or 0 for h in hd_ra_list)

    # ====================================================
    # HÓA ĐƠN RA – CÙNG KỲ NĂM TRƯỚC
    # ====================================================
    hd_ra_lastyear = db.query(models.HoaDonRa).filter(
        models.HoaDonRa.ma_so_thue_nguoi_ban == mst,
        models.HoaDonRa.ngay_lap >= prev_start,
        models.HoaDonRa.ngay_lap <= prev_end
    ).all()

    so_hd_ra_lastyear = len(hd_ra_lastyear)
    tong_hd_ra_lastyear = sum(h.tong_tien_thanh_toan or 0 for h in hd_ra_lastyear)

    # =========================
    # TÍNH CHÊNH LỆCH
    # =========================
    chenhlech = (tong_hd_ra or 0) - (tong_hd_ra_lastyear or 0)

    if abs(chenhlech) >= warning_limit:
        canh_bao = "NGUY HIỂM – Chênh lệch vượt mức cảnh báo!"
    else:
        canh_bao = "Bình thường"

    # =========================
    # TRẢ VỀ KẾT QUẢ
    # =========================
    return schemas.ReconcileHDR(
        ma_so_thue=mst,
        khoang_thoi_gian=date_label,

        # Năm nay
        so_hd_ra=so_hd_ra,
        tong_hd_ra=tong_hd_ra,

        # Năm trước
        so_hd_ra_lastyear=so_hd_ra_lastyear,
        tong_hd_ra_lastyear=tong_hd_ra_lastyear,

        # Chênh lệch
        chenhlech=chenhlech,
        canh_bao=canh_bao,

        # Chi tiết hóa đơn
        hoa_don_ra=[schemas.HoaDonRaSchema.from_orm(h) for h in hd_ra_list],
        hoa_don_ra_lastyear=[schemas.HoaDonRaSchema.from_orm(h) for h in hd_ra_lastyear],
    )

@router.get("/doi_chieu_hdv_cung_ky", response_model=schemas.ReconcileHDV)
def reconcile_invoice_vao(
    mst: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    warning_limit: Optional[float] = 1_000_000_000,
    db: Session = Depends(get_db)
):
    # =========================
    # XỬ LÝ NGÀY
    # =========================
    if start_date and not end_date:
        end_date = date.today()

    if end_date and not start_date:
        start_date = date(2000, 1, 1)

    if not start_date and not end_date:
        start_date = date(2000, 1, 1)
        end_date = date.today()

    # Nhãn khoảng thời gian
    date_label = f"từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"

    # Khoảng thời gian cùng kỳ năm trước
    prev_start = date(start_date.year - 1, start_date.month, start_date.day)
    prev_end = date(end_date.year - 1, end_date.month, end_date.day)

    # ====================================================
    # HÓA ĐƠN VÀO – NĂM NAY
    # ====================================================
    hd_vao_list = db.query(models.HoaDonVao).filter(
        models.HoaDonVao.ma_so_thue_nguoi_mua == mst,
        models.HoaDonVao.ngay_lap >= start_date,
        models.HoaDonVao.ngay_lap <= end_date
    ).all()

    so_hd_vao = len(hd_vao_list)
    tong_hd_vao = sum(h.tong_tien_thanh_toan or 0 for h in hd_vao_list)

    # ====================================================
    # HÓA ĐƠN VÀO – CÙNG KỲ NĂM TRƯỚC
    # ====================================================
    hd_vao_lastyear = db.query(models.HoaDonVao).filter(
        models.HoaDonVao.ma_so_thue_nguoi_mua == mst,
        models.HoaDonVao.ngay_lap >= prev_start,
        models.HoaDonVao.ngay_lap <= prev_end
    ).all()

    so_hd_vao_lastyear = len(hd_vao_lastyear)
    tong_hd_vao_lastyear = sum(h.tong_tien_thanh_toan or 0 for h in hd_vao_lastyear)

    # =========================
    # TÍNH CHÊNH LỆCH
    # =========================
    chenhlech = (tong_hd_vao or 0) - (tong_hd_vao_lastyear or 0)

    if abs(chenhlech) >= warning_limit:
        canh_bao = "NGUY HIỂM – Chênh lệch vượt mức cảnh báo!"
    else:
        canh_bao = "Bình thường"

    # =========================
    # TRẢ VỀ KẾT QUẢ
    # =========================
    return schemas.ReconcileHDV(
        ma_so_thue=mst,
        khoang_thoi_gian=date_label,

        # Năm nay
        so_hd_vao=so_hd_vao,
        tong_hd_vao=tong_hd_vao,

        # Năm trước
        so_hd_vao_lastyear=so_hd_vao_lastyear,
        tong_hd_vao_lastyear=tong_hd_vao_lastyear,

        # Chênh lệch
        chenhlech=chenhlech,
        canh_bao=canh_bao,

        # Chi tiết hóa đơn
        hoa_don_vao=[schemas.HoaDonVaoSchema.from_orm(h) for h in hd_vao_list],
        hoa_don_vao_lastyear=[schemas.HoaDonVaoSchema.from_orm(h) for h in hd_vao_lastyear],
    )
