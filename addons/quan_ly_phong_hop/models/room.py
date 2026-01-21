from odoo import models, fields, api


class RoomMeeting(models.Model):
    _name = 'room.meeting'
    _description = 'Thông tin phòng họp'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Tên phòng', required=True)
    ma_phong_hop = fields.Char(string='Mã phòng họp')
    capacity = fields.Integer(string='Sức chứa', default=0)
    location = fields.Char(string='Vị trí (Tầng)')
    active = fields.Boolean(default=True)
    note = fields.Text(string='Ghi chú')



    # phan_bo_ids = fields.One2many(
    #     'phan_bo_tai_san',
    #     'room_id',
    #     string='Tài sản trong phòng',
    #     domain=[('trang_thai', '=', 'in-use'), ('active', '=', True)]
    # )

    tai_san_count = fields.Integer(
        string='Số tài sản',
        compute='_compute_tai_san_count'
    )

    # @api.depends('phan_bo_ids')
    # def _compute_tai_san_count(self):
    #     for room in self:
    #         room.tai_san_count = len(room.phan_bo_ids)

    
