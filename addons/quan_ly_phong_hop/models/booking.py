# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import google.generativeai as genai
import json
import logging
import re

_logger = logging.getLogger(__name__)


class RoomBooking(models.Model):
    _name = 'room.booking'
    _description = 'Lịch đặt phòng họp'

    # ===== Thông tin cơ bản =====
    name = fields.Char(string='Mục đích họp', required=True)
    start_time = fields.Datetime(string='Bắt đầu', required=True)
    end_time = fields.Datetime(string='Kết thúc', required=True)

    employee_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên đặt phòng',
        required=True
    )

    room_id = fields.Many2one(
        'room.meeting',
        string='Phòng họp'
        required=True
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirm', 'Đã xác nhận'),
        ('cancel', 'Đã hủy')
    ], default='draft')

    # ===== Thành phần tham dự =====
    participant_ids = fields.One2many(
        'room.booking.participant',
        'booking_id',
        string='Thành phần tham dự'
    )

    participant_count = fields.Integer(
        string='Số người tham dự',
        compute='_compute_participant_count',
        store=True
    )

    @api.depends('participant_ids.employee_id')
    def _compute_participant_count(self):
        for rec in self:
            rec.participant_count = len(
                set(rec.participant_ids.mapped('employee_id').ids)
            )

    # ===== Dịch vụ & phê duyệt =====
    service_ids = fields.One2many(
        'room.booking.service',
        'booking_id'
    )

    approval_ids = fields.One2many(
        'room.booking.approval',
        'booking_id'
    )

    # ===== AI fields =====
    ai_room_id = fields.Many2one(
        'room.meeting',
        string='Phòng AI gợi ý',
        readonly=True
    )

    ai_reason = fields.Text(
        string='Lý do AI',
        readonly=True
    )

    # ===== Action =====
    def action_confirm(self):
        for booking in self:
            if booking.state != 'draft':
                continue
            booking.state = 'confirm'
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    # ===== AI Recommend =====
    def action_ai_recommend(self):
        self.ensure_one()

        if self.participant_count <= 0:
            raise ValidationError("Chưa có người tham dự để AI gợi ý phòng")

        api_key = self.env['ir.config_parameter'].sudo().get_param('gemini.api.key')
        if not api_key:
            raise ValidationError("Chưa cấu hình Gemini API Key")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        rooms = self.env['room.meeting'].search([])

        room_data = []
        for r in rooms:
            conflict = self.search([
                ('id', '!=', self.id),
                ('room_id', '=', r.id),
                ('state', '!=', 'cancel'),
                ('start_time', '<', self.end_time),
                ('end_time', '>', self.start_time),
            ], limit=1)

            room_data.append({
                "id": r.id,
                "name": r.name,
                "capacity": r.capacity,
                "busy": bool(conflict)
            })

        prompt = f"""
Bạn là hệ thống AI gợi ý phòng họp trong doanh nghiệp.

Thông tin cuộc họp:
- Số người tham dự: {self.participant_count}
- Thời gian: {self.start_time} đến {self.end_time}

Danh sách phòng (busy = true là đã có lịch):
{json.dumps(room_data, ensure_ascii=False)}

Yêu cầu:
- Chỉ chọn phòng có busy = false
- Sức chứa >= số người tham dự
- Nếu nhiều phòng phù hợp, chọn phòng có sức chứa nhỏ nhất nhưng vẫn đủ

Chỉ trả về JSON hợp lệ:
{{
  "recommended_room_id": number,
  "reason": string
}}
"""

        try:
            response = model.generate_content(prompt)
            text = response.text.strip()

            _logger.info("Gemini raw response: %s", text)

            match = re.search(r'\{.*\}', text, re.S)
            if not match:
                raise ValueError("AI không trả về JSON hợp lệ")

            result = json.loads(match.group())

            room_id = result.get("recommended_room_id")
            room = self.env['room.meeting'].browse(room_id)

            if not room.exists():
                raise ValidationError("AI trả về phòng không hợp lệ")

            self.ai_room_id = room.id
            self.ai_reason = result.get("reason")

        except Exception as e:
            _logger.exception("Lỗi gọi Gemini")
            raise ValidationError(f"Lỗi AI: {str(e)}")

    # ===== Ràng buộc chống trùng phòng =====
    @api.constrains('room_id', 'start_time', 'end_time', 'state')
    def _check_room_booking_overlap(self):
        for booking in self:
            if not booking.room_id or not booking.start_time or not booking.end_time:
                continue

            if booking.state == 'cancel':
                continue

            conflict = self.search([
                ('id', '!=', booking.id),
                ('room_id', '=', booking.room_id.id),
                ('state', '!=', 'cancel'),
                ('start_time', '<', booking.end_time),
                ('end_time', '>', booking.start_time),
            ], limit=1)

            if conflict:
                raise ValidationError(
                    f"Phòng '{booking.room_id.name}' đã được đặt "
                    f"từ {conflict.start_time} đến {conflict.end_time}."
                )
