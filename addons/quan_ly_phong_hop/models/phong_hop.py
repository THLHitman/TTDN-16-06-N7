from odoo import models, fields, api


class PhongHop(models.Model):
    _name = 'phong_hop'
    _description = 'Danh sách phòng họp'

    ma_phong_hop = fields.Char(string='Mã phòng họp', required=True)
    ten_phong_hop = fields.Char(string='Tên phòng họp', required=True)
    suc_chua = fields.Integer(string='Sức chứa', required=True)
    trang_thai = fields.Selection([
        ('trong', 'Trống'),
        ('da_dat', 'Đã đặt'),
        ('dang_su_dung', 'Đang sử dụng')
    ], string='Trạng thái', required=True)
    thiet_bi = fields.Text(string='Thiết bị')
    ghi_chu = fields.Text(string='Ghi chú')
    