from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class LuanChuyenTaiSan(models.Model):
    _name = 'luan_chuyen_tai_san'
    _description = 'Bảng chứa thông tin Luân chuyển tài sản'
    _rec_name = 'ma_phieu_luan_chuyen'
    _order = 'thoi_gian_luan_chuyen desc'
    _sql_constraints = [
        ("ma_phieu_luan_chuyen_unique", "unique(ma_phieu_luan_chuyen)", "Mã phiếu lưu chuyển đã tồn tại !"),
    ]

    ma_phieu_luan_chuyen = fields.Char('Mã phiếu', default='LCTS-', required=True)
    thoi_gian_luan_chuyen = fields.Datetime('Thời gian luân chuyển', required=True, default=fields.Datetime.now)
    ghi_chu = fields.Char('Lý do luân chuyển', default='', required=True)

    loai_nguon = fields.Selection([
        ('phong_ban', 'Phòng ban'),
        ('phong_hop', 'Phòng họp')
    ], string='Nguồn từ', default='phong_ban', required=True)

    loai_dich = fields.Selection([
        ('phong_ban', 'Phòng ban'),
        ('phong_hop', 'Phòng họp')
    ], string='Chuyển tới', default='phong_ban', required=True)

    bo_phan_nguon = fields.Many2one('phong_ban', string='Bộ phận hiện tại', ondelete='restrict')
    phong_hop_nguon = fields.Many2one('room.meeting', string='Phòng họp hiện tại', ondelete='restrict')

    bo_phan_dich = fields.Many2one('phong_ban', string='Bộ phận nhận', ondelete='restrict')
    phong_hop_dich = fields.Many2one('room.meeting', string='Phòng họp nhận', ondelete='restrict')

    luan_chuyen_line_ids = fields.One2many('luan_chuyen_tai_san_line', 'luan_chuyen_id', string='Danh sách tài sản')

    @api.onchange('loai_nguon', 'bo_phan_nguon', 'phong_hop_nguon')
    def _onchange_nguon(self):
        self.luan_chuyen_line_ids = [(5, 0, 0)]

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            for line in record.luan_chuyen_line_ids:
                phan_bo = line.phan_bo_tai_san_id
                if not phan_bo:
                    continue

                write_vals = {
                    'ngay_phat': fields.Date.today(),
                    'ghi_chu': f"Luân chuyển theo phiếu {record.ma_phieu_luan_chuyen}",
                }

                if record.loai_dich == 'phong_hop' and record.phong_hop_dich:
                    write_vals.update({
                        'room_id': record.phong_hop_dich.id,
                        'phong_ban_id': False,
                    })
                elif record.loai_dich == 'phong_ban' and record.bo_phan_dich:
                    write_vals.update({
                        'phong_ban_id': record.bo_phan_dich.id,
                        'room_id': False,
                    })
                
                phan_bo.write(write_vals)
        return records
