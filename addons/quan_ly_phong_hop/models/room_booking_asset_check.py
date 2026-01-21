from odoo import models, fields, api


class RoomBookingAssetCheck(models.Model):
    _name = 'room.booking.asset.check'
    _description = 'Kiểm tra tài sản phòng họp'
    _order = 'check_time desc'

    booking_id = fields.Many2one(
        'room.booking',
        string='Lịch họp',
        required=True,
        ondelete='cascade'
    )

 
#     phan_bo_tai_san_id = fields.Many2one(
#         'phan_bo_tai_san',
#         string='Bản ghi phân bổ',
#         required=True,
#         ondelete='restrict'
#     )


#     tai_san_id = fields.Many2one(
#         'tai_san', 
#         related='phan_bo_tai_san_id.tai_san_id',
#         string='Tài sản gốc',
#         store=True,
#         readonly=True
#     )

    check_type = fields.Selection([
        ('before', 'Trước họp'),
        ('after', 'Sau họp')
    ], required=True)

    state = fields.Selection([
        ('ok', 'Bình thường'),
        ('broken', 'Hư hỏng'),
        ('missing', 'Thiếu')
    ], required=True, default='ok')

    note = fields.Text(string='Ghi chú')
    check_time = fields.Datetime(
        string='Thời điểm kiểm tra',
        default=fields.Datetime.now
    )
