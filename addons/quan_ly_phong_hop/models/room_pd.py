from odoo import models, fields, api
class RoomBookingApproval(models.Model):
    _name = 'room.booking.approval'
    _description = 'Phê duyệt đặt phòng'
    booking_id = fields.Many2one('room.booking')
    approved_by = fields.Many2one('nhan_vien', string='Người duyệt')
    approved_date = fields.Datetime('Ngày duyệt', default=fields.Datetime.now)
    state = fields.Selection([('pending', 'Chờ duyệt'), ('approved', 'Đã duyệt'), ('refused', 'Từ chối')], string='Trạng thái')