from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class DangKyThueSchema(BaseModel):
    co_quan_thue: Optional[str]
    ten_co_quan_thue: Optional[str]
    nguoi_nop_thue: Optional[str]
    ma_so_thue: str
    ten_nguoi_nop_thue: Optional[str]
    ma_nganh_nghe_kd_chinh: Optional[str]
    ten_nganh_nghe_kd_chinh: Optional[str]
    so_nha_duong_pho: Optional[str]
    ma_phuong_xa: Optional[str]
    ten_phuong_xa: Optional[str]
    ma_quan_huyen: Optional[str]
    ten_quan_huyen: Optional[str]
    ma_tinh_thanh_pho: Optional[str]
    ten_tinh_thanh_pho: Optional[str]
    ma_quoc_gia: Optional[str]
    ten_quoc_gia: Optional[str]
    tong_so_lao_dong: Optional[int]
    nganh_nghe_kinh_doanh: Optional[str]
    ten_giam_doc: Optional[str]
    dien_thoai_giam_doc: Optional[str]
    ten_ke_toan_truong: Optional[str]
    dien_thoai_ke_toan_truong: Optional[str]
    so_giay_to: Optional[str]
    ngay_cap: Optional[date]
    loai_giay_to: Optional[str]
    so_giay_thong_hanh: Optional[str]
    so_the_quan_nhan: Optional[str]
    so_cmnd_nguoi_dai_dien: Optional[str]
    so_giay_to_khac: Optional[str]
    phuong_phap_tinh_thue: Optional[str]
    so_cmnd_chu_doanh_nghiep: Optional[str]
    so_giay_chung_nhan_dkkd: Optional[str]
    ngay_cap_giay_chung_nhan_dkkd: Optional[date]
    so_quyet_dinh_thanh_lap: Optional[str]
    ngay_quyet_dinh_thanh_lap: Optional[date]
    so_hop_dong: Optional[str]
    ngay_cap_hop_dong: Optional[date]
    co_chi_nhanh: Optional[bool]
    so_cmnd: Optional[str]
    so_ho_chieu: Optional[str]
    chuong: Optional[str]
    khoan: Optional[str]
    loai_nguoi_nop_thue: Optional[str]
    trang_thai_dkt_ca_nhan: Optional[str]
    trang_thai_dkt_to_chuc: Optional[str]
    ngay_nhan_to_khai: Optional[date]
    loai_hinh_kinh_te: Optional[str]
    tam_nghi_tu_ngay: Optional[date]
    tam_nghi_den_ngay: Optional[date]
    ly_do_tam_nghi: Optional[str]
    ly_do_dong_mst_ca_nhan: Optional[str]
    ngay_dong_trang_thai_ca_nhan: Optional[date]
    ly_do_dong_mst_to_chuc: Optional[str]
    ngay_dong_trang_thai_to_chuc: Optional[date]
    noi_sinh: Optional[str]
    quoc_tich: Optional[str]
    ngay_sinh: Optional[date]
    so_ho_chieu_chu_doanh_nghiep: Optional[str]
    so_the_quan_nhan_chu_doanh_nghiep: Optional[str]
    so_giay_thong_hanh_chu_doanh_nghiep: Optional[str]
    von_kinh_doanh: Optional[Decimal]
    nguon_von_nsnn: Optional[Decimal]
    nguon_von_nuoc_ngoai: Optional[Decimal]
    nguon_von_khac: Optional[Decimal]
    ngay_bat_dau_kinh_doanh: Optional[date]
    dien_thoai_ban: Optional[str]
    so_may_le: Optional[str]
    dien_thoai_di_dong: Optional[str]
    dia_chi_email: Optional[str]
    so_tai_khoan: Optional[str]
    ten_ngan_hang: Optional[str]
    ten_ngan_hang_2: Optional[str]
    hinh_thuc_thanh_toan: Optional[str]
    nam_tai_chinh_tu: Optional[date]
    nam_tai_chinh_den: Optional[date]
    email_tb_thue: Optional[str]
    dia_chi_thuc_te_kinh_doanh: Optional[str]
    dien_tich_kinh_doanh: Optional[Decimal]
    so_lao_dong_thuc_te: Optional[int]
    tien_dien_su_dung: Optional[Decimal]
    tien_nuoc_su_dung: Optional[Decimal]
    chi_phi_thue_mat_bang: Optional[Decimal]
    quy_mo_dan_so_dia_ban_kinh_doanh: Optional[int]
    doanh_thu_ke_khai: Optional[float]

    class Config:
        orm_mode = True

class TaxCreate(BaseModel):
    ma_so_thue: str
    ten_doanh_nghiep: Optional[str]
    dia_chi: Optional[str]
    nganh_nghe: Optional[str]

class TaxUpdate(BaseModel):
    ten_doanh_nghiep: Optional[str]
    dia_chi: Optional[str]
    nganh_nghe: Optional[str]

class TaxOut(BaseModel):
    id: int
    ma_so_thue: str
    ten_doanh_nghiep: str
    dia_chi: str
    nganh_nghe: str

    class Config:
        from_attributes = True
        orm_mode = True
        

class PaginatedTax(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[DangKyThueSchema]

class HoaDonRaBase(BaseModel):
    ky_hieu_mau_so: Optional[str]
    ky_hieu_hoa_don: Optional[str]
    so_hoa_don: Optional[str]
    ngay_lap: Optional[date]

    ma_so_thue_nguoi_ban: Optional[str]
    ten_nguoi_ban: Optional[str]

    ma_so_thue_nguoi_mua: Optional[str]
    ten_nguoi_mua: Optional[str]
    dia_chi_nguoi_mua: Optional[str]

    ma_so_thue_to_chuc_cung_cap_giai_phap: Optional[str]
    ma_so_thue_to_chuc_truyen_nhan: Optional[str]

    tong_tien_chua_thue: Optional[float]
    tong_tien_thue: Optional[float]
    tong_tien_chiet_khau_tm: Optional[float]
    tong_tien_phi: Optional[float]
    tong_tien_thanh_toan: Optional[float]

    don_vi_tien_te: Optional[str]
    ty_gia: Optional[float]

    trang_thai_hoa_don: Optional[str]
    ket_qua_kiem_tra_hoa_don: Optional[str]


class HoaDonRaCreate(HoaDonRaBase):
    pass


class HoaDonRaUpdate(HoaDonRaBase):
    pass


class HoaDonRaSchema(HoaDonRaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        
class HoaDonVaoBase(BaseModel):
    ky_hieu_mau_so: Optional[str]
    ky_hieu_hoa_don: Optional[str]
    so_hoa_don: Optional[str]
    ngay_lap: Optional[date]

    ma_so_thue_nguoi_ban: Optional[str]
    ten_nguoi_ban: Optional[str]
    dia_chi_nguoi_ban: Optional[str]

    ma_so_thue_nguoi_mua: str  # bắt buộc
    ten_nguoi_mua: Optional[str]

    ma_so_thue_to_chuc_cung_cap_giai_phap: Optional[str]
    ma_so_thue_to_chuc_truyen_nhan: Optional[str]

    tong_tien_chua_thue: Optional[float]
    tong_tien_thue: Optional[float]
    tong_tien_chiet_khau_tm: Optional[float]
    tong_tien_phi: Optional[float]
    tong_tien_thanh_toan: Optional[float]

    don_vi_tien_te: Optional[str]
    ty_gia: Optional[float]

    trang_thai_hoa_don: Optional[str]
    ket_qua_kiem_tra_hoa_don: Optional[str]


class HoaDonVaoCreate(HoaDonVaoBase):
    pass


class HoaDonVaoUpdate(HoaDonVaoBase):
    pass


class HoaDonVaoSchema(HoaDonVaoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        
# schemas.py
class ReconcileResult(BaseModel):
    ma_so_thue: str
    so_hd_vao: int
    so_hd_ra: int
    tong_hd_vao: float
    tong_hd_ra: float
    chenhlech: float
    khoang_thoi_gian: str
    canh_bao: str
    
    hoa_don_vao: List[HoaDonVaoSchema]
    hoa_don_ra: List[HoaDonRaSchema]

class ReconcileResult_HDR_Doanh_thu(BaseModel):
    ma_so_thue: str
    so_hd_ra: int
    tong_hd_ra: float
    doanh_thu_ke_khai: float
    chenhlech: float
    khoang_thoi_gian: str
    canh_bao: str
    
    hoa_don_ra: List[HoaDonRaSchema]
    
class ReconcileResult_HDV_Doanh_thu(BaseModel):
    ma_so_thue: str
    so_hd_vao: int
    tong_hd_vao: float
    doanh_thu_ke_khai: float
    chenhlech: float
    khoang_thoi_gian: str
    canh_bao: str
    
    hoa_don_vao: List[HoaDonVaoSchema]
