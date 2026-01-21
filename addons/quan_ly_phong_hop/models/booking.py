# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RoomBooking(models.Model):
    _name = 'room.booking'
    _description = 'Lịch đặt phòng họp'

    name = fields.Char(string='Mục đích họp', required=True)
    start_time = fields.Datetime(string='Bắt đầu', required=True)
    end_time = fields.Datetime(string='Kết thúc', required=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirm', 'Đã xác nhận'),
        ('cancel', 'Đã hủy')
    ], string='Trạng thái', default='draft')

    # asset_check_ids = fields.One2many('room.booking.asset.check','booking_id',string='Kiểm tra tài sản')
    room_id = fields.Many2one('room.meeting', string='Phòng họp', required=True)
    participant_ids = fields.One2many('room.booking.participant', 'booking_id', string='Người tham gia')
    service_ids = fields.One2many('room.booking.service', 'booking_id', string='Dịch vụ đi kèm')
    approval_ids = fields.One2many('room.booking.approval', 'booking_id', string='Lịch sử phê duyệt')
    employee_id = fields.Many2one('nhan_vien', string='Nhân viên đặt phòng', required=True)



    def action_confirm(self):
        """Hàm xử lý khi bấm nút Xác nhận"""
        for record in self:
            if record.state == 'draft':
                record.state = 'confirm'
        return True

    def action_cancel(self):
        """Hàm xử lý khi bấm nút Hủy (nên thêm để đầy đủ logic)"""
        for record in self:
            record.state = 'cancel'
        return True

    def action_confirm(self):
        for booking in self:
            if booking.state != 'draft':
                continue

            assets = self.env['phan_bo_tai_san'].search([
                ('room_id', '=', booking.room_id.id),
                ('trang_thai', '=', 'in-use'),
                ('active', '=', True)
            ])
            for pb in assets:
                self.env['room.booking.asset.check'].create({
                    'booking_id': booking.id,
                    'phan_bo_tai_san_id': pb.id,
                    'check_type': 'before',
                    'state': 'ok'
                })
            
            booking.state = 'confirm'
        return True
    
    @api.constrains('state')
    def _check_after_meeting_asset(self):
        for rec in self:
            if rec.state == 'done':
                after_checks = rec.asset_check_ids.filtered(
                    lambda x: x.check_type == 'after'
                )
                if not after_checks:
                    raise ValidationError(
                        'Phải kiểm tra tài sản SAU họp trước khi hoàn tất.'
                    )