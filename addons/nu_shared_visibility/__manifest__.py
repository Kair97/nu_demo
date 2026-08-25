{
    'name': 'NU Shared Cooperation Visibility',
    'version': '1.0',
    'summary': 'Every NU staff member sees the full partner-cooperation picture',
    'category': 'Customer Relationship Management',
    'author': 'Nazarbayev University — Industry Engagement Office',
    'depends': ['base', 'crm', 'project'],
    'data': [
        'security/nu_visibility.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'description': """
Odoo's stock CRM assumes a competitive sales floor: a salesperson sees only their
own opportunities ("User: Own Documents Only"). That is the wrong model for a
university Industry Engagement Office, where the entire point is a *shared*
registry -- any staff member should be able to open a partner company and see the
complete relationship: who else is working with them, on what, and at what stage.

This module makes that the default by having every internal user automatically
inherit Odoo's stock "Sales / User: All Documents" group, and by making projects
visible to all internal users rather than only invited followers.

Nothing custom is invented here -- it only wires together groups Odoo already
ships. Uninstall it to go back to per-salesperson siloing.
""",
}
