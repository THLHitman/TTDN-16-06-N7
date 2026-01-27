{
    'name': 'Quản lý phòng họp',
    'version': '1.0',
    'summary': 'Đặt phòng họp và tích hợp tài sản',
    'depends': ['base','nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/room_view.xml',
        'views/booking_view.xml',
        'views/dat_phong.xml',
        'views/qlvp.xml',
    ],
    'installable': True,
    'application': True,
}