from odoo import models, fields, api

class RoomBookingParticipant(models.Model):
    _name = 'room.booking.participant'
    _description = 'Người tham gia họp'
    booking_id = fields.Many2one('room.booking', string='Lịch đặt phòng')
    employee_id = fields.Many2one('nhan_vien', string='Nhân viên')