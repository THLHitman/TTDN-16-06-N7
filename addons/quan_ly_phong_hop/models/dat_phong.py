from odoo import models, fields, api


class DatPhong(models.Model):
    _name = 'dat_phong'
    _description = 'Danh sách đặt phòng họp'

    ma_dat_phong = fields.Char(string='Mã đặt phòng', required=True)
    ma_phong_hop = fields.Char(string='Mã phòng họp', required=True)
    ten_phong_hop = fields.Char(string='Tên phòng họp', required=True)
    nguoi_dat = fields.Char(string='Người đặt', required=True)
    ngay_dat = fields.Date(string='Ngày đặt', required=True)
    muc_dich = fields.Text(string='Mục đích', required=True)
    ghi_chu = fields.Text(string='Ghi chú')
    