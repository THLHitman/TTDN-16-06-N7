from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PhanBoTaiSan(models.Model):
    _name = 'phan_bo_tai_san'
    _description = 'Phân bổ tài sản'
    _order = 'ngay_phat desc, id desc'
    _rec_name = 'display_name'

    # =====================
    # Fields
    # =====================
    tai_san_id = fields.Many2one(
        'tai_san',
        string='Tài sản',
        required=True,
        ondelete='cascade',
        index=True
    )

    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban',
        ondelete='restrict',
        index=True
    )

    room_id = fields.Many2one(
        'room.meeting',
        string='Phòng họp',
        ondelete='set null',
        index=True
    )

    nhan_vien_su_dung_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên sử dụng',
        ondelete='restrict',
        index=True
    )

    ngay_phat = fields.Date(
        string='Ngày phân bổ',
        required=True,
        default=fields.Date.today,
        index=True
    )

    trang_thai = fields.Selection([
        ('in-use', 'Đang sử dụng'),
        ('not-in-use', 'Không sử dụng')
    ], string='Trạng thái', required=True, default='in-use', index=True)

    ghi_chu = fields.Text('Ghi chú')
    active = fields.Boolean(default=True)

    display_name = fields.Char(
        compute='_compute_display_name',
        store=False
    )

    # =====================
    # SQL Constraints
    # =====================
    _sql_constraints = [
        (
            'tai_san_unique_active',
            "unique(tai_san_id) "
            "WHERE active=true AND trang_thai='in-use'",
            'Tài sản này đang được sử dụng ở một nơi khác!'
        )
    ]

    # =====================
    # Python Constraints
    # =====================
    @api.constrains('ngay_phat')
    def _check_ngay_phat(self):
        for record in self:
            if record.ngay_phat and record.ngay_phat > fields.Date.today():
                raise ValidationError(
                    _('Ngày phân bổ không được là ngày tương lai!')
                )

    @api.constrains('phong_ban_id', 'room_id')
    def _check_target(self):
        for rec in self:
            if rec.phong_ban_id and rec.room_id:
                raise ValidationError(
                    _('Tài sản chỉ được phân bổ cho Phòng ban HOẶC Phòng họp.')
                )
            if not rec.phong_ban_id and not rec.room_id:
                raise ValidationError(
                    _('Phải chọn Phòng ban hoặc Phòng họp.')
                )
                
    # @api.depends('tai_san_id', 'phong_ban_id', 'room_id')
    # def _compute_display_name(self):
    #     for record in self:
    #         parts = []

    #         if record.tai_san_id:
    #             parts.append(record.tai_san_id.cus_rec_name)

    #         if record.phong_ban_id:
    #             parts.append(record.phong_ban_id.ten_phong_ban)

    #         if record.room_id:
    #             parts.append(record.room_id.name)

    #         record.display_name = " - ".join(parts) if parts else _("Phân bổ mới")
