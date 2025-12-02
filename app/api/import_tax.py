from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
import pandas as pd
import datetime
from io import BytesIO
import re

router = APIRouter()

# ---------------------------
# Hàm chuẩn hóa MST
# ---------------------------
def clean_mst(value):
    if value is None:
        return None
    # Chỉ giữ lại các chữ số
    return "".join(filter(str.isdigit, str(value)))

# ---------------------------
# Hàm parse ngày chuẩn
# ---------------------------
def parse_date(value):
    if value is None or str(value).strip() == "" or str(value).strip().lower() in ["nan", "none", "null"]:
        return None

    # Nếu là datetime hoặc date
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.date() if isinstance(value, datetime.datetime) else value

    # Nếu là serial number của Excel
    if isinstance(value, (int, float)):
        try:
            return datetime.date(1899, 12, 30) + datetime.timedelta(days=int(value))
        except:
            return None

    s = str(value).strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except:
            pass
    return None

# ---------------------------
# API import Excel
# ---------------------------
@router.post("/danh_ba")
def import_excel(file: UploadFile, db: Session = Depends(get_db)):
    try:
        # đọc Excel
        #df = pd.read_excel(file.file)
        contents = file.file.read()
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không đọc được file Excel: {e}")

    # Mapping header Excel → cột SQL
    excel_to_sql = {
        "Mã số thuế": "ma_so_thue",
        "Cơ quan thuế": "co_quan_thue",
        "Tên cơ quan thuế": "ten_co_quan_thue",
        "Người nộp thuế": "nguoi_nop_thue",
        "Tên người nộp thuế": "ten_nguoi_nop_thue",
        "Mã ngành nghề KD chính": "ma_nganh_nghe_kd_chinh",
        "Tên ngành nghề KD chính": "ten_nganh_nghe_kd_chinh",
        "Số nhà/đường/phố": "so_nha_duong_pho",
        "Mã phường/xã": "ma_phuong_xa",
        "Tên phường/xã": "ten_phuong_xa",
        "Mã quận/huyện": "ma_quan_huyen",
        "Tên quận/huyện": "ten_quan_huyen",
        "Mã tỉnh/thành phố": "ma_tinh_thanh_pho",
        "Tên tỉnh/thành phố": "ten_tinh_thanh_pho",
        "Mã quốc gia": "ma_quoc_gia",
        "Tên quốc gia": "ten_quoc_gia",
        "Tổng số lao động": "tong_so_lao_dong",
        "Ngành nghề kinh doanh": "nganh_nghe_kinh_doanh",
        "Tên giám đốc": "ten_giam_doc",
        "Điện thoại giám đốc": "dien_thoai_giam_doc",
        "Tên kế toán trưởng": "ten_ke_toan_truong",
        "Điện thoại kế toán trưởng": "dien_thoai_ke_toan_truong",
        "Số giấy tờ": "so_giay_to",
        "Ngày cấp": "ngay_cap",
        "Loại giấy tờ": "loai_giay_to",
        "Số giấy thông hành": "so_giay_thong_hanh",
        "Số thẻ quân nhân": "so_the_quan_nhan",
        "Số CMND người đại diện": "so_cmnd_nguoi_dai_dien",
        "Phương pháp tính thuế": "phuong_phap_tinh_thue",
        "Ngày sinh": "ngay_sinh",
        "Ngày bắt đầu kinh doanh": "ngay_bat_dau_kinh_doanh",
        "Năm tài chính từ": "nam_tai_chinh_tu",
        "Năm tài chính đến": "nam_tai_chinh_den",
        # ... thêm các cột khác theo nhu cầu
    }

    # Danh sách trường ngày cần parse
    date_fields = [
        "ngay_cap", "ngay_nhan_to_khai", "ngay_sinh", "ngay_bat_dau_kinh_doanh",
        "ngay_cap_giay_chung_nhan_dkkd", "ngay_quyet_dinh_thanh_lap", "ngay_cap_hop_dong",
        "tam_nghi_tu_ngay", "tam_nghi_den_ngay", "ngay_dong_trang_thai_ca_nhan",
        "ngay_dong_trang_thai_to_chuc", "nam_tai_chinh_tu", "nam_tai_chinh_den"
    ]

    count_insert = 0
    count_update = 0

    for idx, row in df.iterrows():
        row_data = {}
        for excel_col, sql_col in excel_to_sql.items():
            if excel_col in row:
                row_data[sql_col] = row[excel_col]

        # Parse các trường ngày
        for f in date_fields:
            if f in row_data:
                row_data[f] = parse_date(row_data[f])
        
        # Kiểm tra mã số thuế
        mst = row_data.get("ma_so_thue")
        mst = clean_mst(mst)
        if not mst:
            continue  # bỏ qua nếu MST rỗng
        row_data["ma_so_thue"] = mst  # ghi lại MST đã chuẩn hóa

        db_obj = db.query(models.DangKyThue).filter(models.DangKyThue.ma_so_thue == mst).first()

        if db_obj:
            # Cập nhật các trường có dữ liệu
            for k, v in row_data.items():
                if v is not None:
                    setattr(db_obj, k, v)
            db.add(db_obj)
            count_update += 1
        else:
            # Chuyển None cho các trường không có trong Excel
            for col in models.DangKyThue.__table__.columns.keys():
                if col not in row_data:
                    row_data[col] = None
            db_obj = models.DangKyThue(**row_data)
            db.add(db_obj)
            count_insert += 1

    db.commit()
    return {"status": "ok", "inserted": count_insert, "updated": count_update}

@router.post("/hoa_don_ra")
def import_hoa_don(file: UploadFile, db: Session = Depends(get_db)):
    try:
        contents = file.file.read()
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không đọc được file Excel: {e}")

    # Mapping header Excel → cột SQL
    excel_to_sql = {
        "Ký hiệu mẫu số": "ky_hieu_mau_so",
        "Ký hiệu hóa đơn": "ky_hieu_hoa_don",
        "Số hóa đơn": "so_hoa_don",
        "Ngày lập": "ngay_lap",
        "MST người bán": "ma_so_thue_nguoi_ban",
        "Tên người bán": "ten_nguoi_ban",
        "MST người mua": "ma_so_thue_nguoi_mua",
        "Tên người mua": "ten_nguoi_mua",
        "Địa chỉ người mua": "dia_chi_nguoi_mua",
        "MST tổ chức cung cấp giải pháp": "ma_so_thue_to_chuc_cung_cap_giai_phap",
        "MST tổ chức truyền nhận": "ma_so_thue_to_chuc_truyen_nhan",
        "Tổng tiền chưa thuế": "tong_tien_chua_thue",
        "Tổng tiền thuế": "tong_tien_thue",
        "Tổng tiền chiết khấu TM": "tong_tien_chiet_khau_tm",
        "Tổng tiền phí": "tong_tien_phi",
        "Tổng tiền thanh toán": "tong_tien_thanh_toan",
        "Đơn vị tiền tệ": "don_vi_tien_te",
        "Tỷ giá": "ty_gia",
        "Trạng thái hóa đơn": "trang_thai_hoa_don",
        "Kết quả kiểm tra hóa đơn": "ket_qua_kiem_tra_hoa_don"
    }

    date_fields = ["ngay_lap"]

    count_insert = 0
    count_update = 0

    for idx, row in df.iterrows():
        row_data = {}
        for excel_col, sql_col in excel_to_sql.items():
            if excel_col in row:
                row_data[sql_col] = row[excel_col]

        # Parse ngày
        for f in date_fields:
            if f in row_data:
                row_data[f] = parse_date(row_data[f])

        # Chuẩn hóa MST
        for mst_field in ["ma_so_thue_nguoi_ban", "ma_so_thue_nguoi_mua"]:
            if mst_field in row_data:
                row_data[mst_field] = clean_mst(row_data[mst_field])

        # Kiểm tra bản ghi đã tồn tại theo so_hoa_don + MST người bán
        so_hoa_don = row_data.get("so_hoa_don")
        ma_so_thue_nguoi_ban = row_data.get("ma_so_thue_nguoi_ban")

        if not (so_hoa_don and ma_so_thue_nguoi_ban):
            continue  # bỏ qua nếu thiếu key chính

        db_obj = db.query(models.HoaDonRa).filter(
            models.HoaDonRa.so_hoa_don == so_hoa_don,
            models.HoaDonRa.ma_so_thue_nguoi_ban == ma_so_thue_nguoi_ban
        ).first()

        if db_obj:
            # Cập nhật các trường có dữ liệu
            for k, v in row_data.items():
                if v is not None:
                    setattr(db_obj, k, v)
            db.add(db_obj)
            count_update += 1
        else:
            # Thêm mới, trường không có dữ liệu → None
            for col in models.HoaDonRa.__table__.columns.keys():
                if col not in row_data:
                    row_data[col] = None
            db_obj = models.HoaDonRa(**row_data)
            db.add(db_obj)
            count_insert += 1

    db.commit()
    return {"status": "ok", "inserted": count_insert, "updated": count_update}


import logging
logger = logging.getLogger("uvicorn")

def safe_float(val):
    try:
        if pd.isna(val):
            return None
        return float(val)
    except:
        return None


@router.post("/hoa_don_vao")
def import_hoa_don_vao(file: UploadFile, db: Session = Depends(get_db)):
    try:
        contents = file.file.read()
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không đọc được file Excel: {e}")

    excel_to_sql = {
        "Ký hiệu mẫu số": "ky_hieu_mau_so",
        "Ký hiệu hóa đơn": "ky_hieu_hoa_don",
        "Số hóa đơn": "so_hoa_don",
        "Ngày lập": "ngay_lap",
        "MST người bán/MST người xuất hàng": "ma_so_thue_nguoi_ban",
        "Tên người bán": "ten_nguoi_ban",
        "Địa chỉ người bán": "dia_chi_nguoi_ban",
        "MST người mua/MST người nhận hàng": "ma_so_thue_nguoi_mua",
        "Tên người mua": "ten_nguoi_mua",
        "MST tổ chức cung cấp giải pháp": "ma_so_thue_to_chuc_cung_cap_giai_phap",
        "MST tổ chức truyền nhận": "ma_so_thue_to_chuc_truyen_nhan",
        "Tổng tiền chưa thuế": "tong_tien_chua_thue",
        "Tổng tiền thuế": "tong_tien_thue",
        "Tổng tiền chiết khấu TM": "tong_tien_chiet_khau_tm",
        "Tổng tiền phí": "tong_tien_phi",
        "Tổng tiền thanh toán": "tong_tien_thanh_toan",
        "Đơn vị tiền tệ": "don_vi_tien_te",
        "Tỷ giá": "ty_gia",
        "Trạng thái hóa đơn": "trang_thai_hoa_don",
        "Kết quả kiểm tra hóa đơn": "ket_qua_kiem_tra_hoa_don"
    }

    numeric_fields = [
        "tong_tien_chua_thue",
        "tong_tien_thue",
        "tong_tien_chiet_khau_tm",
        "tong_tien_phi",
        "tong_tien_thanh_toan",
        "ty_gia",
        "ky_hieu_mau_so"
    ]

    date_fields = ["ngay_lap"]

    count_insert = 0
    count_update = 0
    mst_inserted = set()

    for idx, row in df.iterrows():
        row_data = {}

        for excel_col, sql_col in excel_to_sql.items():
            if excel_col in row:
                row_data[sql_col] = row[excel_col]

        # parse ngày
        for f in date_fields:
            if f in row_data:
                row_data[f] = parse_date(row_data[f])

        # chuẩn hóa MST
        for mst_field in ["ma_so_thue_nguoi_ban", "ma_so_thue_nguoi_mua"]:
            if mst_field in row_data:
                row_data[mst_field] = clean_mst(row_data[mst_field])

        # ép kiểu float
        for f in numeric_fields:
            if f in row_data:
                row_data[f] = safe_float(row_data[f])

        so_hoa_don = row_data.get("so_hoa_don")
        ma_so_thue_nguoi_mua = row_data.get("ma_so_thue_nguoi_mua")

        if not (so_hoa_don and ma_so_thue_nguoi_mua):
            continue

        db_obj = db.query(models.HoaDonVao).filter(
            models.HoaDonVao.so_hoa_don == so_hoa_don,
            models.HoaDonVao.ma_so_thue_nguoi_mua == ma_so_thue_nguoi_mua
        ).first()

        if db_obj:
            for k, v in row_data.items():
                if v is not None:
                    setattr(db_obj, k, v)
            db.add(db_obj)
            count_update += 1
        else:
            for col in models.HoaDonVao.__table__.columns.keys():
                if col not in row_data:
                    row_data[col] = None
            db_obj = models.HoaDonVao(**row_data)
            db.add(db_obj)
            count_insert += 1
            mst_inserted.add(ma_so_thue_nguoi_mua)

    db.commit()

    logger.info(f"ĐÃ INSERT {count_insert} hóa đơn từ {len(mst_inserted)} MST")
    logger.info(f"DANH SÁCH MST INSERT: {', '.join(mst_inserted)}")

    return {
        "status": "ok",
        "inserted": count_insert,
        "updated": count_update,
        "mst_inserted": list(mst_inserted)
    }



@router.post("/CSDL_KD")
def import_excel(file: UploadFile, db: Session = Depends(get_db)):
    # ==========================
    #  Bước 1: Đọc file upload
    # ==========================
    try:
        contents = file.file.read()
        df_raw = pd.read_excel(BytesIO(contents), header=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không đọc được file Excel: {e}")

    if df_raw.shape[0] < 5:
        raise HTTPException(status_code=400, detail="File Excel không đúng cấu trúc (phải có ≥ 5 dòng).")

    # ==========================
    #  Bước 2: Làm sạch header (4 dòng đầu)
    # ==========================
    df_header = df_raw.iloc[:4].copy()
    df_header = df_header.fillna(method="ffill", axis=0)

    row_main = df_header.iloc[0]   # header cha
    row_sub  = df_header.iloc[3]   # header con

    def format_text(s):
        s = str(s).strip().lower()
        s = re.sub(r'[\n\r]+', ' ', s)
        s = re.sub(r'\s+', ' ', s)
        return s

    headers = []
    for i in range(len(row_main)):
        parent = format_text(row_main[i])
        child  = format_text(row_sub[i])
        headers.append(child if child not in ("", "nan") else parent)

    # ==========================
    #  Bước 3: Giữ nguyên dữ liệu
    # ==========================
    df = df_raw.iloc[4:, :].reset_index(drop=True)
    df.columns = headers

    # ==========================
    #  Mapping Excel → DB column
    # ==========================
    excel_to_sql = {
        "mst": "ma_so_thue",
        "cơ quan thuế": "co_quan_thue",
        "tên cơ quan thuế": "ten_co_quan_thue",
        "người nộp thuế": "nguoi_nop_thue",
        "tên người nộp thuế": "ten_nguoi_nop_thue",
        "mã ngành nghề kd chính": "ma_nganh_nghe_kd_chinh",
        "tên ngành nghề kd chính": "ten_nganh_nghe_kd_chinh",
        "số nhà/đường/phố": "so_nha_duong_pho",
        "mã phường/xã": "ma_phuong_xa",
        "tên phường/xã": "ten_phuong_xa",
        "mã quận/huyện": "ma_quan_huyen",
        "tên quận/huyện": "ten_quan_huyen",
        "mã tỉnh/thành phố": "ma_tinh_thanh_pho",
        "tên tỉnh/thành phố": "ten_tinh_thanh_pho",
        "mã quốc gia": "ma_quoc_gia",
        "tên quốc gia": "ten_quoc_gia",
        "tổng số lao động": "tong_so_lao_dong",
        "ngành nghề kinh doanh": "nganh_nghe_kinh_doanh",
        "tên giám đốc": "ten_giam_doc",
        "điện thoại giám đốc": "dien_thoai_giam_doc",
        "tên kế toán trưởng": "ten_ke_toan_truong",
        "điện thoại kế toán trưởng": "dien_thoai_ke_toan_truong",
        "số giấy tờ": "so_giay_to",
        "ngày cấp": "ngay_cap",
        "loại giấy tờ": "loai_giay_to",
        "số giấy thông hành": "so_giay_thong_hanh",
        "số thẻ quân nhân": "so_the_quan_nhan",
        "số cmnd người đại diện": "so_cmnd_nguoi_dai_dien",
        "phương pháp tính thuế": "phuong_phap_tinh_thue",
        "ngày sinh": "ngay_sinh",
        "ngày bắt đầu kinh doanh": "ngay_bat_dau_kinh_doanh",
        "năm tài chính từ": "nam_tai_chinh_tu",
        "năm tài chính đến": "nam_tai_chinh_den",
        "doanh thu trên tờ khai": "doanh_thu_ke_khai"
    }

    date_fields = [
        "ngay_cap", "ngay_sinh", "ngay_bat_dau_kinh_doanh",
        "nam_tai_chinh_tu", "nam_tai_chinh_den"
    ]

    count_insert = 0
    count_update = 0

    # ==========================
    #  Bước 4: Lặp từng dòng import
    # ==========================
    for idx, row in df.iterrows():
        row_data = {}

        for excel_col, sql_col in excel_to_sql.items():
            if excel_col in df.columns:
                row_data[sql_col] = row.get(excel_col)

        # Parse ngày
        for f in date_fields:
            if f in row_data:
                row_data[f] = parse_date(row_data[f])

        # Chuẩn hóa MST
        mst = clean_mst(row_data.get("ma_so_thue"))
        if not mst:
            continue

        row_data["ma_so_thue"] = mst

        # Kiểm tra DB
        db_obj = db.query(models.DangKyThue)\
                   .filter(models.DangKyThue.ma_so_thue == mst)\
                   .first()

        if db_obj:
            # Cập nhật chỉ những trường có giá trị
            for k, v in row_data.items():
                if v not in (None, "", "nan"):
                    setattr(db_obj, k, v)
            db.add(db_obj)
            count_update += 1

        else:
            # Gán None cho cột không có trong Excel
            for col in models.DangKyThue.__table__.columns.keys():
                if col not in row_data:
                    row_data[col] = None

            db_obj = models.DangKyThue(**row_data)
            db.add(db_obj)
            count_insert += 1

    db.commit()

    return {
        "status": "ok",
        "inserted": count_insert,
        "updated": count_update,
        "total": count_insert + count_update
    }