from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RoomBookingParticipant(models.Model):
    _name = 'room.booking.participant'
    _description = 'Thành phần tham dự'

    booking_id = fields.Many2one('room.booking', required=True, ondelete='cascade')
    employee_id = fields.Many2one('nhan_vien', string='Nhân viên', required=True)

    @api.constrains('employee_id', 'booking_id')
    def _check_trung_nhan_vien(self):
        for rec in self:
            if not rec.employee_id or not rec.booking_id:
                continue

            dup = self.search_count([
                ('booking_id', '=', rec.booking_id.id),
                ('employee_id', '=', rec.employee_id.id),
                ('id', '!=', rec.id),
            ])

            if dup > 0:
                raise ValidationError(
                    f"Nhân viên {rec.employee_id.display_name} đã được thêm vào cuộc họp."
                )
