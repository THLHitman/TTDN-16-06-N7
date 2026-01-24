from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
    start_time = fields.Datetime(string='Bắt đầu', required=True)
    end_time = fields.Datetime(string='Kết thúc', required=True)

    @api.constrains('ma_phong_hop', 'start_time', 'end_time')
    def _check_trung_phong(self):
        for rec in self:
            if rec.start_time >= rec.end_time:
                raise ValidationError("Thời gian kết thúc phải lớn hơn thời gian bắt đầu.")

            domain = [
                ('id', '!=', rec.id),
                ('ma_phong_hop', '=', rec.ma_phong_hop),
                ('start_time', '<', rec.end_time),
                ('end_time', '>', rec.start_time),
            ]

            if self.search(domain, limit=1):
                raise ValidationError(
                    f"Phòng '{rec.ten_phong_hop}' đã được đặt trong khoảng thời gian này."
                )
