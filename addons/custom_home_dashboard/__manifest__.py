{
    'name': 'Custom Home Dashboard',
    'version': '2.0',
    'summary': 'Enterprise-style Home Menu (app grid) for Odoo Community',
    'category': 'Productivity',
    'author': 'Nazarbayev University — Industry Engagement Office',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'custom_home_dashboard/static/src/dashboard/dashboard.scss',
            'custom_home_dashboard/static/src/dashboard/dashboard.js',
            'custom_home_dashboard/static/src/dashboard/dashboard.xml',
            'custom_home_dashboard/static/src/home_menu/home_menu_service.js',
            'custom_home_dashboard/static/src/home_menu/webclient_patch.js',
            'custom_home_dashboard/static/src/navbar/navbar_patch.js',
            'custom_home_dashboard/static/src/navbar/navbar_patch.xml',
            'custom_home_dashboard/static/src/navbar/navbar_patch.scss',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'description': """
Brings Odoo Enterprise's Home Menu experience to Community: a searchable grid of
app icons on a full-screen dark background, toggled from the navbar.

Implemented the same way Enterprise does it -- as a real client action registered
under the tag "menu" -- rather than as a floating overlay. That tag is
special-cased by Odoo's router, so the URL becomes a bare "/odoo", refreshing
keeps you on the home menu, and browser back/forward work normally.
""",
}
