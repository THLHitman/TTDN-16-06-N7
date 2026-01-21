# Odoo 15 Asset Management (Quản Lý Tài Sản) - AI Agent Instructions

## Project Overview
This is an **Odoo 15 ERP instance** with a custom Vietnamese asset management module (`quan_ly_tai_san`). The codebase combines Odoo core with custom modules for managing company assets, depreciation, allocation, and borrowing/lending workflows.

**Tech Stack:** Python 3.8+, PostgreSQL, Odoo Framework 15, XML Views, JavaScript

---

## Architecture & Core Concepts

### Module Structure
Each addon follows this standard Odoo pattern:
```
addon_name/
├── __manifest__.py          # Module metadata, dependencies, data files to load
├── models/__init__.py       # Import all model classes
├── models/*.py              # Business logic (ORM models, computations, constraints)
├── views/                   # XML view definitions (forms, trees, searches)
├── security/
│   └── ir.model.access.csv  # Row-level security rules per model
├── controllers/             # Web routes (if applicable)
├── static/                  # CSS, JavaScript assets
└── demo/                    # Demo data
```

### Critical Models in `quan_ly_tai_san`
- **`tai_san`** — Core asset record with code, name, purchase date, depreciation settings
- **`phan_bo_tai_san`** — Asset allocation linking asset → department/employee/room
- **`danh_muc_tai_san`** — Asset category classification
- **`muon_tra_tai_san`** — Borrowing/lending transactions and state tracking
- **`lich_su_khau_hao`** — Depreciation history
- **`room.meeting`** — Classroom/meeting rooms (from `nhan_su` dependency)

### Data Flow Pattern
1. **Create Asset** (`tai_san`) → Assign Category → Set Depreciation Method
2. **Allocate Asset** (`phan_bo_tai_san`) → Link to Department/Employee → Assign Location/Room
3. **Record Transactions** → Borrow/Return, Liquidation, Transfer
4. **Track Depreciation** → Auto-compute or manual logging

---

## Key Development Conventions

### Model Field Definitions
- **Many2one relations:** Always include `ondelete` policy (`cascade`, `restrict`, `set null`)
  ```python
  tai_san_id = fields.Many2one('tai_san', required=True, ondelete='cascade')
  phong_ban_id = fields.Many2one('phong_ban', required=True, ondelete='restrict')
  ```
- **Computed fields:** Always use `@api.depends()` and `store=True` for frequent queries
  ```python
  display_name = fields.Char(compute='_compute_display_name', store=True)
  ```
- **Selections:** Use tuple list with lowercase dash-separated keys
  ```python
  trang_thai = fields.Selection([('in-use', 'Đang sử dụng'), ('not-in-use', 'Không sử dụng')])
  ```

### Constraints & Validation
- Use `@api.constrains()` for business rule validation (not database checks)
  ```python
  @api.constrains('ngay_phat')
  def _check_ngay_phat(self):
      if record.ngay_phat > fields.Date.today():
          raise ValidationError(_('Ngày phân bổ không được là ngày tương lai!'))
  ```
- SQL constraints for uniqueness: `_sql_constraints = [('constraint_name', 'SQL_EXPR', 'Message')]`

### Onchange Methods
- **Avoid returning values directly** — use `return {'value': {...}}` pattern
- **Fields triggering onchange must exist** — if field is `None` or `_unknown`, accessing `.id` will fail
- **Example error:** `AttributeError: '_unknown' object has no attribute 'id'` means a Many2one field was not properly initialized during create/write before onchange triggered

### XML View Patterns
- **Form groups:** Use `col="2"` for 2-column layout, nested `<group>` for organization
- **Many2one domain filtering:** Apply constraints to filter valid related records
  ```xml
  <field name="tai_san_id" domain="[('trang_thai_thanh_ly', 'in', ['chua_phan_bo', 'chua_thanh_ly'])]"/>
  ```
- **Tree decorations:** Use `decoration-muted`, `decoration-danger` for visual cues
  ```xml
  <tree decoration-muted="trang_thai == 'not-in-use'">
  ```
- **Search filters & grouping:** Define in `<search>` view using domain and group_by context

### Python/SQL Conventions
- **File naming:** Use snake_case: `phan_bo_tai_san.py`, `tai_san.py`
- **Class naming:** Use PascalCase matching model intent: `PhanBoTaiSan`, `TaiSan`
- **Model name:** Use lowercase `_name = 'phan_bo_tai_san'` (dots for namespacing: `module.model`)
- **Field names:** Vietnamese snake_case: `ngay_phat`, `vi_tri_tai_san_id`
- **_rec_name:** Define a custom display field (not always `name`) — used in dropdowns
  ```python
  _rec_name = 'cus_rec_name'  # Custom display computation
  ```

### Security Model
- Every model requires `ir.model.access.csv` entry with format: `module.modelname,modelname,model_id,group_id,perm_read,perm_create,perm_write,perm_unlink`
- Example: `quan_ly_tai_san.access_tai_san,tai_san,quan_ly_tai_san.model_tai_san,base.group_user,1,1,1,1`

---

## Common Tasks & Patterns

### Adding a New Asset-Related Model
1. Create `models/new_model.py` with class inheriting `models.Model`
2. Import in `models/__init__.py`
3. Add to `__manifest__.py` data list: `'views/new_model.xml'`
4. Create XML view file with form/tree/search records
5. Add `security/ir.model.access.csv` entry
6. Update `menu.xml` if user-facing

### Linking Related Records
- Use Many2one with appropriate `domain` constraints in views
- In Python: `self.relation_id` returns the related record (avoid accessing undefined fields)
- **Safe field access:** Always check existence before accessing related record attributes
  ```python
  if self.tai_san_id and self.tai_san_id.id:
      # Safe to use self.tai_san_id.field_name
  ```

### Running & Testing
- **Start server:** `python3 odoo-bin.py -c odoo.conf`
- **Update module:** Add `-u module_name` flag to update module after code changes
- **Create test database:** Use `docker-compose up -d` to spin up PostgreSQL
- **Config file:** Uses `odoo.conf` with db connection, port, addon paths

---

## Debugging Common Issues

### AttributeError: '_unknown' object has no attribute 'id'
**Cause:** Onchange method tries to access `.id` on a Many2one field that hasn't been properly set during form initialization.
**Solution:** 
- Check if field is required but not initialized in create()
- Use `if record.field_id:` before accessing `.field_id.attribute`
- Ensure domain filters don't exclude all valid options

### Module Import Errors
- Verify `__manifest__.py` lists all model files in dependencies
- Check circular imports in `models/__init__.py`
- Ensure XML file paths in `data:` list are relative to addon root

### SQL Constraint Violations
- Check `_sql_constraints` definitions match actual field states
- Unique constraints with WHERE clause: ensure condition logic is clear
- Test constraint with raw SQL before committing

---

## File References for Common Patterns
- Core model patterns: [models/tai_san.py](../addons/quan_ly_tai_san/models/tai_san.py), [models/phan_bo_tai_san.py](../addons/quan_ly_tai_san/models/phan_bo_tai_san.py)
- XML form/view examples: [views/phan_bo_tai_san.xml](../addons/quan_ly_tai_san/views/phan_bo_tai_san.xml)
- Security setup: [security/ir.model.access.csv](../addons/quan_ly_tai_san/security/ir.model.access.csv)
- Module manifest template: [__manifest__.py](../addons/quan_ly_tai_san/__manifest__.py)

---

## External Integration Notes
- **Dependencies:** `quan_ly_tai_san` depends on `nhan_su` module (HR/Employee system)
- **Room linking:** Uses `room.meeting` model from HR module for classroom assignment
- **Depreciation:** Custom `lich_su_khau_hao` implements both linear and declining depreciation

---

## Quick Reference Commands
```bash
# Start Odoo with module updates
python3 odoo-bin.py -c odoo.conf -u quan_ly_tai_san --dev=all

# Create/reset database
createdb -h localhost -U odoo your_db_name

# Check module status via CLI
python3 odoo-bin.py -c odoo.conf scaffold new_module addons/
```
