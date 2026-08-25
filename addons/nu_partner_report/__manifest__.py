{
    'name': 'NU Partner Cooperation Report',
    'version': '1.0',
    'summary': 'One-click PDF report of everything NU does with a partner company',
    'category': 'Customer Relationship Management',
    'author': 'Nazarbayev University — Industry Engagement Office',
    'depends': ['base', 'contacts', 'crm', 'project', 'calendar'],
    'data': [
        'report/partner_cooperation_report.xml',
        'report/partner_cooperation_templates.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'description': """
Adds a "Cooperation Report" PDF to any partner company, pulling together the full
relationship history in one professional document:

* company profile and all contact persons
* every CRM opportunity, grouped by cooperation direction (R&D, internships,
  sponsorship, corporate training, consulting, events, academic partnerships,
  consortiums), with revenue, stage, probability and responsible person
* all projects and their tasks/subtasks linked to the company
* meetings, visits and calls on record
* which NU staff are involved in the relationship

Print it from Contacts: open a company -> Print -> Cooperation Report.
""",
}
