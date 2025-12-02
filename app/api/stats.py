from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from app.database import get_db
from app import models, schemas
import numpy as np

router = APIRouter()

@router.get("/tan_suat_hoa_don", response_model=List[schemas.TanSuatHoaDon])
def tan_suat_hoa_don(
    mst: List[str] = Query(...),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    risk_days: int = 7,
    db: Session = Depends(get_db)
):

    # --- Xử lý ngày ---
    if start_date and not end_date:
        end_date = date.today()

    if end_date and not start_date:
        start_date = date(2000, 1, 1)

    if not start_date and not end_date:
        start_date = date(2000, 1, 1)
        end_date = date.today()

    so_ngay = (end_date - start_date).days + 1

    results = []

    for ma_so in mst:

        # ========================================================================
        # 1. HÓA ĐƠN RA
        # ========================================================================
        query_ra = db.query(models.HoaDonRa).filter(
            models.HoaDonRa.ma_so_thue_nguoi_ban == ma_so,
            models.HoaDonRa.ngay_lap >= start_date,
            models.HoaDonRa.ngay_lap <= end_date
        )

        hd_ra = query_ra.all()
        so_hd_ra = len(hd_ra)

        # Danh sách ngày có hóa đơn RA
        ngay_ra = sorted(set([h.ngay_lap for h in hd_ra if h.ngay_lap]))

        # Tính chuỗi ngày không phát sinh hóa đơn RA
        longest_gap_ra = 0
        if ngay_ra:
            prev = start_date
            for d in ngay_ra:
                diff = (d - prev).days
                if diff > longest_gap_ra:
                    longest_gap_ra = diff
                prev = d
            longest_gap_ra = max(longest_gap_ra, (end_date - ngay_ra[-1]).days)
        else:
            longest_gap_ra = so_ngay

        canh_bao_ra = (
            f"Cảnh báo: ≥ {risk_days} ngày liên tiếp không phát sinh hóa đơn RA"
            if longest_gap_ra >= risk_days else "Bình thường"
        )

        # ========================================================================
        # 2. HÓA ĐƠN VÀO
        # ========================================================================
        query_vao = db.query(models.HoaDonVao).filter(
            models.HoaDonVao.ma_so_thue_nguoi_mua == ma_so,
            models.HoaDonVao.ngay_lap >= start_date,
            models.HoaDonVao.ngay_lap <= end_date
        )

        hd_vao = query_vao.all()
        so_hd_vao = len(hd_vao)

        # Danh sách ngày có hóa đơn VÀO
        ngay_vao = sorted(set([h.ngay_lap for h in hd_vao if h.ngay_lap]))

        # Tính chuỗi ngày không phát sinh hóa đơn VÀO
        longest_gap_vao = 0
        if ngay_vao:
            prev = start_date
            for d in ngay_vao:
                diff = (d - prev).days
                if diff > longest_gap_vao:
                    longest_gap_vao = diff
                prev = d
            longest_gap_vao = max(longest_gap_vao, (end_date - ngay_vao[-1]).days)
        else:
            longest_gap_vao = so_ngay

        canh_bao_vao = (
            f"Cảnh báo: ≥ {risk_days} ngày liên tiếp không phát sinh hóa đơn VÀO"
            if longest_gap_vao >= risk_days else "Bình thường"
        )

        # ========================================================================
        # 3. PHÂN LOẠI TRẠNG THÁI HÓA ĐƠN
        # ========================================================================
        all_hd = hd_ra + hd_vao

        so_hd_moi = sum(1 for h in all_hd if h.trang_thai_hoa_don and "mới" in h.trang_thai_hoa_don.lower())
        so_hd_dc = sum(1 for h in all_hd if h.trang_thai_hoa_don and "điều chỉnh" in h.trang_thai_hoa_don.lower())
        so_hd_tt = sum(1 for h in all_hd if h.trang_thai_hoa_don and "thay thế" in h.trang_thai_hoa_don.lower())
        so_hd_huy = sum(1 for h in all_hd if h.trang_thai_hoa_don and "hủy" in h.trang_thai_hoa_don.lower())

        tong_hd = len(all_hd)

        # ========================================================================
        # 4. TÍNH TRUNG BÌNH NGÀY / 1 HÓA ĐƠN (RIÊNG RA & RIÊNG VÀO)
        # ========================================================================
        tb_ngay_1_hd_ra = so_ngay / so_hd_ra if so_hd_ra > 0 else 0
        tb_ngay_1_hd_vao = so_ngay / so_hd_vao if so_hd_vao > 0 else 0

        # ========================================================================
        # 5. TRẢ KẾT QUẢ
        # ========================================================================
        result = schemas.TanSuatHoaDon(
            mst=ma_so,
            so_ngay=so_ngay,

            # Hóa đơn RA
            so_hoa_don_ra=so_hd_ra,
            trung_binh_ngay_1_hd_ra=tb_ngay_1_hd_ra,
            longest_gap_ra=longest_gap_ra,
            canh_bao_ra=canh_bao_ra,

            # Hóa đơn VÀO
            so_hoa_don_vao=so_hd_vao,
            trung_binh_ngay_1_hd_vao=tb_ngay_1_hd_vao,
            longest_gap_vao=longest_gap_vao,
            canh_bao_vao=canh_bao_vao,

            # Phân loại trạng thái
            tong_hoa_don=tong_hd,
            so_hoa_don_moi=so_hd_moi,
            so_hoa_don_dieu_chinh=so_hd_dc,
            so_hoa_don_thay_the=so_hd_tt,
            so_hoa_don_huy=so_hd_huy,
        )

        results.append(result)

    return results

@router.get("/kiem_tra_rui_ro_hd", response_model=List[schemas.RuiRoHoaDon])
def kiem_tra_rui_ro_hoa_don(
    mst: Optional[List[str]] = Query(None),   # nếu None → lấy tất cả MST
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    risk_days: int = 7,
    db: Session = Depends(get_db)
):

    # --- Xử lý ngày ---
    if start_date and not end_date:
        end_date = date.today()

    if end_date and not start_date:
        start_date = date(2000, 1, 1)

    if not start_date and not end_date:
        start_date = date(2000, 1, 1)
        end_date = date.today()

    # Nếu không nhập MST → lấy tất cả MST từ bảng đăng ký thuế
    if not mst:
        mst = [r.ma_so_thue for r in db.query(models.DangKyThue.ma_so_thue).all()]

    results = []

    # Tổng số ngày trong khoảng
    so_ngay = (end_date - start_date).days + 1

    for ma_so in mst:

        # ============================
        #       HÓA ĐƠN RA
        # ============================
        hd_ra = db.query(models.HoaDonRa).filter(
            models.HoaDonRa.ma_so_thue_nguoi_ban == ma_so,
            models.HoaDonRa.ngay_lap >= start_date,
            models.HoaDonRa.ngay_lap <= end_date
        ).all()

        # Không có hoá đơn RA
        khong_co_hd_ra = (len(hd_ra) == 0)

        # Tính khoảng trống liên tiếp lớn nhất
        days_ra = sorted(set([h.ngay_lap for h in hd_ra if h.ngay_lap]))
        longest_gap_ra = 0

        if days_ra:
            prev = start_date
            for d in days_ra:
                gap = (d - prev).days
                longest_gap_ra = max(longest_gap_ra, gap)
                prev = d

            longest_gap_ra = max(longest_gap_ra, (end_date - days_ra[-1]).days)
        else:
            longest_gap_ra = so_ngay

        canh_bao_ra = (
            f"Rủi ro: {longest_gap_ra} ngày không xuất hóa đơn RA"
            if longest_gap_ra >= risk_days else None
        )

        # ============================
        #       HÓA ĐƠN VÀO
        # ============================
        hd_vao = db.query(models.HoaDonVao).filter(
            models.HoaDonVao.ma_so_thue_nguoi_mua == ma_so,
            models.HoaDonVao.ngay_lap >= start_date,
            models.HoaDonVao.ngay_lap <= end_date
        ).all()

        khong_co_hd_vao = (len(hd_vao) == 0)

        days_vao = sorted(set([h.ngay_lap for h in hd_vao if h.ngay_lap]))
        longest_gap_vao = 0

        if days_vao:
            prev = start_date
            for d in days_vao:
                gap = (d - prev).days
                longest_gap_vao = max(longest_gap_vao, gap)
                prev = d

            longest_gap_vao = max(longest_gap_vao, (end_date - days_vao[-1]).days)

        else:
            longest_gap_vao = so_ngay

        canh_bao_vao = (
            f"Rủi ro: {longest_gap_vao} ngày không phát sinh hóa đơn VÀO"
            if longest_gap_vao >= risk_days else None
        )

        # ============================
        #       KẾT QUẢ
        # ============================
        results.append(
            schemas.RuiRoHoaDon(
                mst=ma_so,
                khong_co_hd_ra=khong_co_hd_ra,
                khong_co_hd_vao=khong_co_hd_vao,
                khoang_trong_hd_ra=longest_gap_ra,
                khoang_trong_hd_vao=longest_gap_vao,
                canh_bao_hd_ra=canh_bao_ra,
                canh_bao_hd_vao=canh_bao_vao
            )
        )

    return results
