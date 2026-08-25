{
    'name': 'NU Shared Cooperation Visibility',
    'version': '1.1',
    'summary': 'Baseline rights so every NU staff account can work on day one',
    'category': 'Customer Relationship Management',
    'author': 'Nazarbayev University — Industry Engagement Office',
    'depends': ['base', 'crm', 'project', 'event', 'survey'],
    'data': [
        'security/nu_visibility.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'description': """
Gives every internal user a sensible baseline of rights, by having the standard
"Internal User" group imply groups Odoo already ships. Nothing custom is invented.

Granted to everyone:

* Sales / User: All Documents -- Odoo's stock CRM assumes a competitive sales
  floor where a salesperson sees only their own opportunities. That is the wrong
  model for an Industry Engagement Office, where the point is a *shared* registry:
  any staff member should be able to open a partner company and see the complete
  relationship, including who else is working with them. Without this, a newly
  created account saw 0 of 26 opportunities.
* Events / User -- staff run career fairs, Industry Days and delegation visits.
* Surveys / User -- staff send partner-satisfaction and intern-feedback surveys.

Deliberately NOT granted to everyone:

* Role / Administrator (base.group_system) -- this is what allows creating users
  and changing system configuration, i.e. full administrative control. Grant it to
  named people only: Settings -> Users & Companies -> Users -> pick the person ->
  Administration = "Settings". The office director should have it, ideally plus one
  backup so nobody is locked out. Everyone else does not need it to do their job.

Uninstall to return to stock Odoo defaults.

MAINTENANCE NOTE
----------------
base.group_user is a "noupdate" record, so Odoo applies changes to it only when
this module is *installed*, and silently skips them on a plain `-u` upgrade.
If you add another group to the list above, it will take effect on a fresh
install but NOT on an upgrade of an existing database. On an existing database
either reinstall this module, or apply the same change once from the shell:

    env.ref('base.group_user').write({
        'implied_ids': [(4, env.ref('<the.group_xmlid>').id)],
    })
""",
}
