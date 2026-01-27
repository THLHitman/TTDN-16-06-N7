from odoo import models, fields, api


class RoomBookingAssetCheck(models.Model):
    _name = 'room.booking.asset.check'
    _description = 'Kiểm tra tài sản phòng họp'
    _order = 'check_time desc'

    