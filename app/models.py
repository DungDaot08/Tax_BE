from sqlalchemy import Column, String, Integer, Date, Boolean, Numeric, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DangKyThue(Base):
    __tablename__ = "dang_ky_thue"

    co_quan_thue = Column(String(255))
    ten_co_quan_thue = Column(String(255))
    nguoi_nop_thue = Column(String(255))
    ma_so_thue = Column(String(50), primary_key=True, index=True)
    ten_nguoi_nop_thue = Column(String(255))
    ma_nganh_nghe_kd_chinh = Column(String(50))
    ten_nganh_nghe_kd_chinh = Column(String(255))
    so_nha_duong_pho = Column(String(255))
    ma_phuong_xa = Column(String(50))
    ten_phuong_xa = Column(String(255))
    ma_quan_huyen = Column(String(50))
    ten_quan_huyen = Column(String(255))
    ma_tinh_thanh_pho = Column(String(50))
    ten_tinh_thanh_pho = Column(String(255))
    ma_quoc_gia = Column(String(50))
    ten_quoc_gia = Column(String(255))
    tong_so_lao_dong = Column(Integer)
    nganh_nghe_kinh_doanh = Column(Text)
    ten_giam_doc = Column(String(255))
    dien_thoai_giam_doc = Column(String(50))
    ten_ke_toan_truong = Column(String(255))
    dien_thoai_ke_toan_truong = Column(String(50))
    so_giay_to = Column(String(255))
    ngay_cap = Column(Date)
    loai_giay_to = Column(String(255))
    so_giay_thong_hanh = Column(String(255))
    so_the_quan_nhan = Column(String(255))
    so_cmnd_nguoi_dai_dien = Column(String(100))
    so_giay_to_khac = Column(String(255))
    phuong_phap_tinh_thue = Column(String(255))
    so_cmnd_chu_doanh_nghiep = Column(String(100))
    so_giay_chung_nhan_dkkd = Column(String(255))
    ngay_cap_giay_chung_nhan_dkkd = Column(Date)
    so_quyet_dinh_thanh_lap = Column(String(255))
    ngay_quyet_dinh_thanh_lap = Column(Date)
    so_hop_dong = Column(String(255))
    ngay_cap_hop_dong = Column(Date)
    co_chi_nhanh = Column(Boolean)
    so_cmnd = Column(String(100))
    so_ho_chieu = Column(String(100))
    chuong = Column(String(50))
    khoan = Column(String(50))
    loai_nguoi_nop_thue = Column(String(255))
    trang_thai_dkt_ca_nhan = Column(String(255))
    trang_thai_dkt_to_chuc = Column(String(255))
    ngay_nhan_to_khai = Column(Date)
    loai_hinh_kinh_te = Column(String(255))
    tam_nghi_tu_ngay = Column(Date)
    tam_nghi_den_ngay = Column(Date)
    ly_do_tam_nghi = Column(Text)
    ly_do_dong_mst_ca_nhan = Column(Text)
    ngay_dong_trang_thai_ca_nhan = Column(Date)
    ly_do_dong_mst_to_chuc = Column(Text)
    ngay_dong_trang_thai_to_chuc = Column(Date)
    noi_sinh = Column(String(255))
    quoc_tich = Column(String(255))
    ngay_sinh = Column(Date)
    so_ho_chieu_chu_doanh_nghiep = Column(String(100))
    so_the_quan_nhan_chu_doanh_nghiep = Column(String(100))
    so_giay_thong_hanh_chu_doanh_nghiep = Column(String(100))
    von_kinh_doanh = Column(Numeric(18, 2))
    nguon_von_nsnn = Column(Numeric(18, 2))
    nguon_von_nuoc_ngoai = Column(Numeric(18, 2))
    nguon_von_khac = Column(Numeric(18, 2))
    ngay_bat_dau_kinh_doanh = Column(Date)
    dien_thoai_ban = Column(String(50))
    so_may_le = Column(String(50))
    dien_thoai_di_dong = Column(String(50))
    dia_chi_email = Column(String(255))
    so_tai_khoan = Column(String(255))
    ten_ngan_hang = Column(String(255))
    ten_ngan_hang_2 = Column(String(255))
    hinh_thuc_thanh_toan = Column(String(255))
    nam_tai_chinh_tu = Column(Date)
    nam_tai_chinh_den = Column(Date)
    email_tb_thue = Column(String(255))
    dia_chi_thuc_te_kinh_doanh = Column(String(255))
    dien_tich_kinh_doanh = Column(Numeric(18, 2))
    so_lao_dong_thuc_te = Column(Integer)
    tien_dien_su_dung = Column(Numeric(18, 2))
    tien_nuoc_su_dung = Column(Numeric(18, 2))
    chi_phi_thue_mat_bang = Column(Numeric(18, 2))
    quy_mo_dan_so_dia_ban_kinh_doanh = Column(Integer)
    doanh_thu_ke_khai = Column(Numeric(18, 2))
    ten_cua_hang = Column(String(255), nullable=True)
    mat_bang_kinh_doanh = Column(String(255), nullable=True)


    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


from sqlalchemy import Column, String, Numeric, Date, Integer, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship


class HoaDonRa(Base):
    __tablename__ = "hoa_don_ra"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    ky_hieu_mau_so = Column(String(50))
    ky_hieu_hoa_don = Column(String(50))
    so_hoa_don = Column(String(50))
    ngay_lap = Column(Date)

    # Người bán / Người xuất hàng
    ma_so_thue_nguoi_ban = Column(String(50), ForeignKey("dang_ky_thue.ma_so_thue"))
    #ma_so_thue_nguoi_ban = Column(String(50))
    ten_nguoi_ban = Column(String(255))

    # Người mua / Người nhận hàng
    ma_so_thue_nguoi_mua = Column(String(50))
    ten_nguoi_mua = Column(String(255))
    dia_chi_nguoi_mua = Column(String(255))

    # Thông tin hệ thống hóa đơn
    ma_so_thue_to_chuc_cung_cap_giai_phap = Column(String(50))
    ma_so_thue_to_chuc_truyen_nhan = Column(String(50))

    # Các giá trị tiền
    tong_tien_chua_thue = Column(Numeric(18, 2))
    tong_tien_thue = Column(Numeric(18, 2))
    tong_tien_chiet_khau_tm = Column(Numeric(18, 2))
    tong_tien_phi = Column(Numeric(18, 2))
    tong_tien_thanh_toan = Column(Numeric(18, 2))

    don_vi_tien_te = Column(String(20))
    ty_gia = Column(Numeric(18, 6))

    trang_thai_hoa_don = Column(String(255))
    ket_qua_kiem_tra_hoa_don = Column(Text)

    # Timestamp
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Quan hệ với bảng dang_ky_thue
    nguoi_ban = relationship("DangKyThue", backref="hoa_don_ra")

class HoaDonVao(Base):
    __tablename__ = "hoa_don_vao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    ky_hieu_mau_so = Column(String(50))
    ky_hieu_hoa_don = Column(String(50))
    so_hoa_don = Column(String(50))
    ngay_lap = Column(Date)

    # Người bán / xuất hàng
    ma_so_thue_nguoi_ban = Column(String(50))
    ten_nguoi_ban = Column(String(255))
    dia_chi_nguoi_ban = Column(String(255))

    # Người mua / nhận hàng (bắt buộc)
    ma_so_thue_nguoi_mua = Column(String(50), ForeignKey("dang_ky_thue.ma_so_thue"), nullable=False)
    #ma_so_thue_nguoi_mua = Column(String(50), nullable=False)
    ten_nguoi_mua = Column(String(255))

    # Thông tin hệ thống hóa đơn
    ma_so_thue_to_chuc_cung_cap_giai_phap = Column(String(50))
    ma_so_thue_to_chuc_truyen_nhan = Column(String(50))

    # Giá trị tiền
    tong_tien_chua_thue = Column(Numeric(18, 2))
    tong_tien_thue = Column(Numeric(18, 2))
    tong_tien_chiet_khau_tm = Column(Numeric(18, 2))
    tong_tien_phi = Column(Numeric(18, 2))
    tong_tien_thanh_toan = Column(Numeric(18, 2))

    don_vi_tien_te = Column(String(20))
    ty_gia = Column(Numeric(18, 6))

    trang_thai_hoa_don = Column(String(255))
    ket_qua_kiem_tra_hoa_don = Column(Text)

    # Timestamp
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Quan hệ với bảng dang_ky_thue
    nguoi_mua = relationship("DangKyThue", backref="hoa_don_vao")
    
class HoKhoan(Base):
    __tablename__ = "ho_khoan"

    ma_so_thue = Column(String(20), primary_key=True, index=True)
    doanh_thu = Column(Numeric(18, 2), nullable=False)