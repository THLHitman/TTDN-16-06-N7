from odoo import models, fields, api
class RoomBookingService(models.Model):
    _name = 'room.booking.service'
    _description = 'Dịch vụ đi kèm'
    booking_id = fields.Many2one('room.booking')
    service_type = fields.Selection([('tea', 'Trà/Cà phê'), ('snack', 'Đồ ăn nhẹ'), ('projector', 'Máy chiếu')], string='Loại dịch vụ')
    note = fields.Text('Ghi chú')