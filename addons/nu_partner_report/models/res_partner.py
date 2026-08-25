from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _cooperation_root(self):
        """The company the report is really about.

        Printing from a child contact (a person) should still produce the
        company-level report, since that is what people actually want to see.
        """
        self.ensure_one()
        return self.parent_id if (self.parent_id and not self.is_company) else self

    def _cooperation_partner_ids(self):
        """Company + all its contact persons.

        Interactions get recorded against whichever partner was handy at the
        time -- sometimes the company, sometimes a specific person there -- so
        the report has to look at both to show a complete history.
        """
        root = self._cooperation_root()
        return (root | root.child_ids).ids

    def get_cooperation_report_data(self):
        """Everything NU has on record with this company, in one structure."""
        root = self._cooperation_root()
        partner_ids = root._cooperation_partner_ids()

        opportunities = self.env['crm.lead'].search(
            [('partner_id', 'in', partner_ids), ('type', '=', 'opportunity')],
            order='expected_revenue desc, id asc',
        )

        # Group by cooperation direction (the CRM team), keeping teams in a
        # stable order so the same company always prints the same way.
        opportunity_groups = []
        for team in opportunities.mapped('team_id').sorted('id'):
            team_opps = opportunities.filtered(lambda o, t=team: o.team_id == t)
            opportunity_groups.append({
                'team': team,
                'opportunities': team_opps,
                'revenue': sum(team_opps.mapped('expected_revenue')),
            })
        unteamed = opportunities.filtered(lambda o: not o.team_id)
        if unteamed:
            opportunity_groups.append({
                'team': False,
                'opportunities': unteamed,
                'revenue': sum(unteamed.mapped('expected_revenue')),
            })

        tasks = self.env['project.task'].search(
            [('partner_id', 'in', partner_ids)], order='date_deadline asc, id asc',
        )
        projects = self.env['project.project'].search([
            '|',
            ('partner_id', 'in', partner_ids),
            ('id', 'in', tasks.mapped('project_id').ids),
        ], order='name asc')

        project_groups = []
        for project in projects:
            project_tasks = tasks.filtered(lambda t, p=project: t.project_id == p)
            # Subtasks are shown nested under their parent, not as siblings.
            top_level = project_tasks.filtered(lambda t: not t.parent_id)
            orphan_subtasks = project_tasks.filtered(
                lambda t, tl=top_level: t.parent_id and t.parent_id not in tl
            )
            project_groups.append({
                'project': project,
                'tasks': top_level | orphan_subtasks,
                'task_count': len(project_tasks),
            })

        events = self.env['calendar.event'].search(
            [('partner_ids', 'in', partner_ids)], order='start desc',
        )

        # "Who from the university works with this company" -- pulled from
        # everywhere a person can be attached, then de-duplicated.
        staff = self.env['res.users']
        staff |= opportunities.mapped('user_id')
        staff |= projects.mapped('user_id')
        for task in tasks:
            staff |= task.user_ids

        won = opportunities.filtered(lambda o: o.stage_id.is_won)

        return {
            'partner': root,
            'contacts': root.child_ids,
            'opportunities': opportunities,
            'opportunity_groups': opportunity_groups,
            'total_revenue': sum(opportunities.mapped('expected_revenue')),
            'won_revenue': sum(won.mapped('expected_revenue')),
            'won_count': len(won),
            'tags': opportunities.mapped('tag_ids').sorted('id'),
            'projects': projects,
            'project_groups': project_groups,
            'tasks': tasks,
            'events': events,
            'staff': staff,
            'currency': self.env.company.currency_id,
            'company': self.env.company,
        }

    def action_print_cooperation_report(self):
        """Print button on the contact form."""
        self.ensure_one()
        return self.env.ref(
            'nu_partner_report.action_report_partner_cooperation'
        ).report_action(self._cooperation_root())
