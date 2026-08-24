{
    'name': 'Custom Home Dashboard',
    'version': '1.0',
    'summary': 'Custom landing dashboard for nu_demo, shown instead of the default app grid',
    'category': 'Productivity',
    'depends': ['web'],
    'data': [
        'views/dashboard_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_home_dashboard/static/src/dashboard/dashboard.scss',
            'custom_home_dashboard/static/src/dashboard/dashboard.js',
            'custom_home_dashboard/static/src/dashboard/dashboard.xml',
            'custom_home_dashboard/static/src/navbar/navbar_patch.js',
            'custom_home_dashboard/static/src/navbar/navbar_patch.xml',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
