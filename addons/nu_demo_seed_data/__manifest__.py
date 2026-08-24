{
    'name': 'NU Demo Seed Data — REMOVE BEFORE PRODUCTION',
    'version': '1.0',
    'summary': 'Nazarbayev University Industry Partnerships demo dataset (contacts, CRM, projects, HR, calendar, surveys)',
    'category': 'Demo Data',
    'depends': ['base', 'contacts', 'crm', 'project', 'hr', 'calendar', 'survey'],
    'data': [],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'description': """
Fictional but realistic demo data for the nu_demo Community sandbox, modeled on a
university industry-partnerships office. Every record this module creates is tracked
via ir.model.data under this module's name, so uninstalling this module cleanly
removes ALL of it — that's the intended way to erase the demo data once real
production data is ready to go in.
""",
}
