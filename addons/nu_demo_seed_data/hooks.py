import logging

_logger = logging.getLogger(__name__)

MODULE = 'nu_demo_seed_data'
DEMO_PASSWORD = 'NuDemo2026!'


def _ref(env, xml_id, model, vals, update=False):
    """Create-or-fetch a record tracked under this module's xml_id.
    Re-running this hook (e.g. module upgrade) will not duplicate records.
    Uninstalling the module deletes everything created this way."""
    IMD = env['ir.model.data']
    existing = IMD.search([('module', '=', MODULE), ('name', '=', xml_id)], limit=1)
    if existing:
        record = env[model].browse(existing.res_id)
        if record.exists():
            if update:
                record.write(vals)
            return record
        existing.unlink()
    record = env[model].create(vals)
    IMD.create({
        'name': xml_id,
        'module': MODULE,
        'model': model,
        'res_id': record.id,
        'noupdate': True,
    })
    return record


def post_init_hook(env):
    _logger.info("nu_demo_seed_data: loading NU Industry Partnerships demo dataset")

    company = _seed_company(env)
    users = _seed_users(env, company)
    departments = _seed_departments(env)
    employees = _seed_employees(env, company, departments, users)
    _seed_department_managers(env, departments, employees)
    partners = _seed_partners(env, company, employees)
    teams = _seed_crm_teams(env, users)
    stages = _seed_crm_stages(env, teams)
    tags = _seed_crm_tags(env)
    _seed_crm_leads(env, partners, teams, stages, tags, users)
    projects = _seed_projects(env, users, partners, company)
    task_stages = _seed_task_stages(env, projects)
    _seed_tasks(env, projects, task_stages, partners, users)
    _seed_calendar_events(env, partners)
    _seed_surveys(env)
    _seed_public_events(env)

    _logger.info("nu_demo_seed_data: done")


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------

def _seed_company(env):
    company = env.company
    kzt = env['res.currency'].search([('name', '=', 'KZT')], limit=1)
    if kzt and not kzt.active:
        kzt.write({'active': True})
    vals = {
        'name': 'Nazarbayev University',
        'website': 'https://nu.edu.kz',
        'email': 'glovopromo4@gmail.com',
        'city': 'Astana',
        'country_id': env.ref('base.kz').id,
    }
    if kzt:
        vals['currency_id'] = kzt.id
    company.write(vals)
    return company


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def _seed_users(env, company):
    group_user = env.ref('base.group_user').id
    group_sale_manager = env.ref('sales_team.group_sale_manager').id
    group_sale_user = env.ref('sales_team.group_sale_salesman').id
    group_project_manager = env.ref('project.group_project_manager').id
    group_project_user = env.ref('project.group_project_user').id

    users = {}

    users['kaiyrzhan'] = _ref(env, 'user_kaiyrzhan', 'res.users', {
        'name': 'Kaiyrzhan Orynbek',
        'login': 'orynbekkajyrzan@gmail.com',
        'email': 'orynbekkajyrzan@gmail.com',
        'password': DEMO_PASSWORD,
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'group_ids': [(6, 0, [group_user, group_sale_manager, group_project_manager])],
    })

    users['madi'] = _ref(env, 'user_madi', 'res.users', {
        'name': 'Мади Мурзатанов',
        'login': 'marystanov@gmail.com',
        'email': 'marystanov@gmail.com',
        'password': DEMO_PASSWORD,
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'group_ids': [(6, 0, [group_user, group_sale_user, group_project_user])],
    })

    users['anargul'] = _ref(env, 'user_anargul', 'res.users', {
        'name': 'Anargul Sandalova',
        'login': 'Anargul.Sandalova@gmail.com',
        'email': 'Anargul.Sandalova@gmail.com',
        'password': DEMO_PASSWORD,
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'group_ids': [(6, 0, [group_user, group_sale_user, group_project_user])],
    })

    return users


# ---------------------------------------------------------------------------
# HR: departments & employees
# ---------------------------------------------------------------------------

DEPARTMENTS = [
    ('dept_admin', 'Administration'),
    ('dept_ieo', 'Офис индустриального взаимодействия'),
    ('dept_it', 'Департамент информационных технологий'),
    ('dept_admissions', 'Приёмная комиссия'),
    ('dept_accred', 'Отдел аккредитации и качества образования'),
]

DEPARTMENT_MANAGERS = {
    'dept_ieo': 'emp_kaiyrzhan',
    'dept_it': 'emp_timur',
    'dept_admissions': 'emp_gulnara',
    'dept_accred': 'emp_zhanna',
}

EMPLOYEES = [
    # key, name, job_title, dept_key, manager_key, work_email, user_key
    ('emp_kaiyrzhan', 'Kaiyrzhan Orynbek', 'Директор офиса индустриального взаимодействия', 'dept_ieo', None, 'orynbekkajyrzan@gmail.com', 'kaiyrzhan'),
    ('emp_madi', 'Мади Мурзатанов', 'Менеджер по консалтингу и партнёрствам', 'dept_ieo', 'emp_kaiyrzhan', 'marystanov@gmail.com', 'madi'),
    ('emp_sara', 'Сара Ким', 'Координатор по спонсорству и мероприятиям', 'dept_ieo', 'emp_kaiyrzhan', 's.kim@nu.edu.kz', None),
    ('emp_daniyar', 'Данияр Ахметов', 'Координатор по корпоративному обучению', 'dept_ieo', 'emp_kaiyrzhan', 'd.akhmetov@nu.edu.kz', None),
    ('emp_bekzat', 'Бекзат Нурланов', 'Координатор по стажировкам и трудоустройству', 'dept_ieo', 'emp_kaiyrzhan', 'b.nurlanov@nu.edu.kz', None),
    ('emp_ainur', 'Айнур Жумабекова', 'Координатор по R&D и совместным лабораториям', 'dept_ieo', 'emp_kaiyrzhan', 'a.zhumabekova@nu.edu.kz', None),
    ('emp_timur', 'Тимур Байжанов', 'Начальник департамента информационных технологий', 'dept_it', None, 't.baizhanov@nu.edu.kz', None),
    ('emp_aliya', 'Алия Сматова', 'Специалист по сетевой инфраструктуре', 'dept_it', 'emp_timur', 'a.smatova@nu.edu.kz', None),
    ('emp_gulnara', 'Гульнара Есенова', 'Начальник приёмной комиссии', 'dept_admissions', None, 'g.yessenova@nu.edu.kz', None),
    ('emp_erlan', 'Ерлан Досов', 'Специалист приёмной комиссии', 'dept_admissions', 'emp_gulnara', 'e.dossov@nu.edu.kz', None),
    ('emp_zhanna', 'Жанна Абенова', 'Начальник отдела аккредитации', 'dept_accred', None, 'zh.abenova@nu.edu.kz', None),
]


def _seed_departments(env):
    departments = {}
    for key, name in DEPARTMENTS:
        departments[key] = _ref(env, key, 'hr.department', {'name': name})
    return departments


def _seed_employees(env, company, departments, users):
    employees = {}
    # first pass: create without manager (some managers are created later in the list)
    for key, name, job_title, dept_key, manager_key, email, user_key in EMPLOYEES:
        vals = {
            'name': name,
            'job_title': job_title,
            'department_id': departments[dept_key].id,
            'work_email': email,
            'company_id': company.id,
        }
        if user_key:
            vals['user_id'] = users[user_key].id
        employees[key] = _ref(env, key, 'hr.employee', vals)

    # second pass: wire up manager (parent_id) now that all employees exist
    for key, name, job_title, dept_key, manager_key, email, user_key in EMPLOYEES:
        if manager_key:
            employees[key].write({'parent_id': employees[manager_key].id})

    return employees


def _seed_department_managers(env, departments, employees):
    for dept_key, emp_key in DEPARTMENT_MANAGERS.items():
        departments[dept_key].write({'manager_id': employees[emp_key].id})


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

# key, name, city, phone, email, website, [(contact_name, job_title), ...]
PARTNER_COMPANIES = [
    ('bi_group', 'BI Group', 'Астана', '+7 7172 91 91 91', 'info@bi.group', 'https://bi.group',
     [('Данияр Сулейменов', 'Директор по персоналу')]),
    ('baker_hughes', 'Baker Hughes Kazakhstan', 'Атырау', '+7 7122 76 00 00', 'kazakhstan@bakerhughes.com', 'https://bakerhughes.com',
     [('Тимур Абенов', 'Технический директор')]),
    ('ey_kz', 'EY Казахстан', 'Алматы', '+7 727 258 59 60', 'dbatyr08@gmail.com', 'https://www.ey.com/kz_kz',
     [('Роман Ким', 'Recruiting Manager')]),
    ('kpmg_kz', 'KPMG Казахстан', 'Алматы', '+7 727 298 08 98', 'almaty@kpmg.kz', 'https://kpmg.com/kz',
     [('Гульнара Ораева', 'Партнёр, консалтинговые услуги'), ('Сергей Пак', 'Партнёр, консалтинг')]),
    ('kaspi', 'Kaspi.kz', 'Алматы', '+7 727 330 40 00', 'info@kaspi.kz', 'https://kaspi.kz',
     [('Айгерим Токсарова', 'CSR & Sponsorship Manager'), ('Руслан Жакупбеков', 'Head of Talent Acquisition')]),
    ('samsung', 'Samsung Electronics Central Eurasia', 'Алматы', '+7 727 258 26 26', 'kz.office@samsung.com', 'https://samsung.com/kz', []),
    ('kazatomprom', 'АО «КазАтомПром»', 'Астана', '+7 7172 45 25 25', 'info@kazatomprom.kz', 'https://kazatomprom.kz', []),
    ('kazakhtelecom', 'АО «Казахтелеком»', 'Астана', '+7 7172 55 66 66', 'info@telecom.kz', 'https://telecom.kz',
     [('Марат Юсупов', 'Директор по развитию бизнеса')]),
    ('kmg', 'АО НК «КазМунайГаз»', 'Астана', '+7 701 234 56 01', 'a.satpayeva@kmg.kz', 'https://kmg.kz',
     [('Айгерим Сатпаева', 'Директор по устойчивому развитию')]),
    ('ktz', 'АО НК «Қазақстан темір жолы» (KTZ)', 'Астана', '+7 7172 60 22 22', 'info@railways.kz', 'https://railways.kz', []),
    ('halyk', 'АО «Народный Банк Казахстана» (Halyk Bank)', 'Алматы', '+7 701 234 56 03', 'd.akhmetova@halykbank.kz', 'https://halykbank.kz',
     [('Динара Ахметова', 'HR Business Partner'), ('Динара Серикқызы', 'HR Business Partner')]),
    ('samruk', 'АО «Самрук-Қазына»', 'Астана', '+7 7172 55 30 00', 'info@sk.kz', 'https://sk.kz',
     [('Гулзада Жупанова', 'Директор по устойчивому развитию')]),
    ('air_astana', 'АО «Эйр Астана» (Air Astana)', 'Алматы', '+7 727 258 42 82', 'info@airastana.com', 'https://airastana.com',
     [('Айгуль Жумагулова', 'Talent Acquisition Lead'), ('Асем Бекова', 'Менеджер по PR')]),
    ('erg', 'Евразийская группа (ERG)', 'Астана', '+7 701 234 56 02', 'e.tulegenov@erg.kz', 'https://erg.kz',
     [('Виктор Ли', 'R&D Partnerships Manager'), ('Ерлан Тулегенов', 'Руководитель отдела инноваций')]),
    ('beeline', 'ТОО «Beeline Казахстан»', 'Алматы', '+7 727 322 22 22', 'info@beeline.kz', 'https://beeline.kz',
     [('Жанна Женжебаева', 'Менеджер по обучению и развитию')]),
    ('tco', 'ТОО «Теңізшевройл» (Tengizchevroil)', 'Атырау', '+7 7122 96 33 33', 'info@tco.kz', 'https://tengizchevroil.com',
     [('Марат Сагындыков', 'Менеджер по работе с вузами')]),
]

# internal NU staff mirrored as standalone contact records (employees not already users)
INTERNAL_STAFF_CONTACT_KEYS = ['emp_sara', 'emp_daniyar', 'emp_bekzat', 'emp_ainur', 'emp_timur', 'emp_aliya', 'emp_gulnara', 'emp_erlan', 'emp_zhanna']


def _seed_partners(env, company, employees):
    kz = env.ref('base.kz').id
    partners = {}

    for key, name, city, phone, email, website, contacts in PARTNER_COMPANIES:
        partner = _ref(env, f'partner_{key}', 'res.partner', {
            'name': name,
            'is_company': True,
            'city': city,
            'phone': phone,
            'email': email,
            'website': website,
            'country_id': kz,
        })
        partners[key] = partner
        for i, (cname, job) in enumerate(contacts):
            _ref(env, f'partner_{key}_contact_{i}', 'res.partner', {
                'name': cname,
                'function': job,
                'parent_id': partner.id,
                'is_company': False,
                'country_id': kz,
            })

    # internal NU staff, as child contacts of the main company partner
    for emp_key in INTERNAL_STAFF_CONTACT_KEYS:
        emp = employees[emp_key]
        _ref(env, f'staff_contact_{emp_key}', 'res.partner', {
            'name': emp.name,
            'function': emp.job_title,
            'parent_id': company.partner_id.id,
            'email': emp.work_email,
            'is_company': False,
            'country_id': kz,
        })

    return partners


# ---------------------------------------------------------------------------
# CRM
# ---------------------------------------------------------------------------

TEAMS = [
    ('team_rd', 'R&D', 'kaiyrzhan', []),
    ('team_training', 'Corporate Training', 'kaiyrzhan', []),
    ('team_sponsorship', 'Sponsorship', 'kaiyrzhan', []),
    ('team_internship', 'Internship', 'kaiyrzhan', ['kaiyrzhan', 'madi']),
    ('team_consulting', 'Консалтинг и экспертиза', 'kaiyrzhan', []),
    ('team_events', 'Мероприятия и визиты', 'kaiyrzhan', []),
    ('team_academic', 'Академические партнёрства', 'kaiyrzhan', []),
    ('team_consortium', 'Консорциумы и стратегические партнёрства', 'kaiyrzhan', []),
]

STAGES_BY_TEAM = {
    'team_rd': ['Новый запрос', 'Оценка осуществимости', 'Предложение по контракту', 'NDA / Юридическая проверка', 'Согласование договора', 'Контракт подписан'],
    'team_training': ['Новый запрос', 'Оценка потребности', 'Коммерческое предложение', 'Согласование договора', 'Программа продана'],
    'team_sponsorship': ['Новая заявка', 'Оценка заявки', 'Согласование условий', 'Спонсорство оформлено'],
    'team_internship': ['Заявка от компании', 'Согласование условий стажировки', 'Договор подписан', 'Идёт набор стажёров', 'Программа завершена'],
    'team_consulting': ['Новый запрос', 'Скоуп и оценка', 'Коммерческое предложение', 'Согласование', 'Сдано'],
    'team_events': ['Идея / заявка', 'Планирование', 'Подтверждено', 'Проведено'],
    'team_academic': ['Инициировано', 'Переговоры', 'Юридическая проверка', 'Подписано'],
    'team_consortium': ['Рассматривается', 'Обсуждение условий членства', 'Одобрение советом', 'Участие оформлено'],
}

TAGS = [
    'Контрактные исследования и R&D',
    'Консалтинг и экспертные услуги',
    'Спонсорство и пожертвования',
    'Корпоративное обучение',
    'Трудоустройство и стажировки',
    'Совместные лаборатории',
    'Adjunct professorship',
    'Лицензирование технологий',
    'Мероприятия и визиты',
    'Консорциумы и партнёрства',
]

# name, partner_key, team_key, stage_name, revenue, probability, owner_key, priority, [tag names]
LEADS = [
    ('Разработка катализатора для нефтепереработки — КазМунайГаз', 'kmg', 'team_rd', 'Согласование договора', 85000000, 0, 'kaiyrzhan', '2', ['Контрактные исследования и R&D']),
    ('R&D проект по цифровизации добычи — Теңізшевройл', 'tco', 'team_rd', 'Предложение по контракту', 60000000, 50, 'madi', '2', ['Контрактные исследования и R&D']),
    ('Лицензирование технологии очистки пластовых вод — КазАтомПром', 'kazatomprom', 'team_rd', 'Контракт подписан', 45000000, 100, 'kaiyrzhan', '2', ['Лицензирование технологий']),
    ('Исследование материалов для аккумуляторов — Samsung Electronics', 'samsung', 'team_rd', 'Оценка осуществимости', 30000000, 50, 'madi', '2', ['Контрактные исследования и R&D']),
    ('Пилотная лаборатория ИИ-мониторинга скважин — Baker Hughes', 'baker_hughes', 'team_rd', 'Новый запрос', 25000000, 50, 'kaiyrzhan', '1', ['Совместные лаборатории']),
    ('Совместная лаборатория геологоразведки — ERG', 'erg', 'team_rd', 'NDA / Юридическая проверка', 120000000, 50, 'kaiyrzhan', '2', ['Совместные лаборатории']),
    ('Корпоративная программа Data Science — Halyk Bank', 'halyk', 'team_training', 'Согласование договора', 18000000, 50, 'kaiyrzhan', '2', ['Корпоративное обучение']),
    ('Курс по кибербезопасности для сотрудников — Казахтелеком', 'kazakhtelecom', 'team_training', 'Коммерческое предложение', 14000000, 50, 'madi', '1', ['Корпоративное обучение']),
    ('Обучение по Agile и проектному менеджменту — Kaspi.kz', 'kaspi', 'team_training', 'Коммерческое предложение', 12000000, 50, 'madi', '1', ['Корпоративное обучение']),
    ('Повышение квалификации инженеров-путейцев — KTZ', 'ktz', 'team_training', 'Оценка потребности', 9500000, 50, 'kaiyrzhan', '0', ['Корпоративное обучение']),
    ('Именная стипендия для студентов — Самрук-Қазына', 'samruk', 'team_sponsorship', 'Согласование условий', 20000000, 50, 'madi', '1', ['Спонсорство и пожертвования']),
    ('Спонсорство Career Fair NU 2026 — Air Astana', 'air_astana', 'team_sponsorship', 'Спонсорство оформлено', 8000000, 100, 'kaiyrzhan', '2', ['Спонсорство и пожертвования', 'Мероприятия и визиты']),
    ('Спонсорская поддержка Startup Weekend NU — Beeline', 'beeline', 'team_sponsorship', 'Согласование условий', 5000000, 50, 'kaiyrzhan', '0', ['Спонсорство и пожертвования', 'Мероприятия и визиты']),
    ('Стажировки для студентов IT-специальностей — EY Казахстан', 'ey_kz', 'team_internship', 'Договор подписан', 0, 50, 'kaiyrzhan', '1', ['Трудоустройство и стажировки']),
    ('Ярмарка вакансий и набор выпускников — Air Astana', 'air_astana', 'team_internship', 'Программа завершена', 0, 100, 'madi', '1', ['Трудоустройство и стажировки']),
    ('Стажировки в отделе разведки и добычи — Теңізшевройл', 'tco', 'team_internship', 'Заявка от компании', 0, 50, 'kaiyrzhan', '0', ['Трудоустройство и стажировки']),
    ('Консультации по цифровой трансформации — Halyk Bank', 'halyk', 'team_consulting', 'Скоуп и оценка', 11000000, 0, 'kaiyrzhan', '1', ['Консалтинг и экспертные услуги']),
    ('Экспертная консультация по ESG-стратегии — KPMG Казахстан', 'kpmg_kz', 'team_consulting', 'Скоуп и оценка', 15000000, 50, 'madi', '2', ['Консалтинг и экспертные услуги']),
    ('Консалтинговый проект по устойчивому строительству — BI Group', 'bi_group', 'team_consulting', 'Новый запрос', 10000000, 50, 'kaiyrzhan', '0', ['Консалтинг и экспертные услуги']),
    ('Industry Day 2026 совместно с ERG', 'erg', 'team_events', 'Подтверждено', 0, 50, 'madi', '1', ['Мероприятия и визиты']),
    ('Визит делегации Tengizchevroil в кампус NU', 'tco', 'team_events', 'Проведено', 0, 100, 'kaiyrzhan', '3', ['Мероприятия и визиты']),
    ('Демо-день студенческих проектов для КазМунайГаз', 'kmg', 'team_events', 'Идея / заявка', 0, 40, 'kaiyrzhan', '0', ['Мероприятия и визиты']),
    ('Adjunct professorship для инженеров-практиков — Baker Hughes', 'baker_hughes', 'team_academic', 'Юридическая проверка', 0, 50, 'kaiyrzhan', '1', ['Adjunct professorship']),
    ('Adjunct professorship для практиков нефтегазовой отрасли — Tengizchevroil', 'tco', 'team_academic', 'Инициировано', 0, 50, 'madi', '3', ['Adjunct professorship']),
    ('Участие в консорциуме Digital Silk Road — Казахтелеком', 'kazakhtelecom', 'team_consortium', 'Одобрение советом', 0, 50, 'madi', '2', ['Консорциумы и партнёрства']),
    ('Консорциум зелёной энергетики — Самрук-Қазына', 'samruk', 'team_consortium', 'Обсуждение условий членства', 0, 50, 'madi', '1', ['Консорциумы и партнёрства']),
]


def _seed_crm_teams(env, users):
    teams = {}
    for key, name, lead_key, member_keys in TEAMS:
        vals = {'name': name, 'user_id': users[lead_key].id}
        team = _ref(env, key, 'crm.team', vals)
        if member_keys:
            try:
                team.write({'member_ids': [(6, 0, [users[k].id for k in member_keys])]})
            except Exception:
                _logger.warning("nu_demo_seed_data: could not set member_ids on team %s", key)
        teams[key] = team
    return teams


# Terminal stages: reaching one of these means the cooperation actually
# happened, which is what makes a deal count as "реализуемая" rather than
# merely "потенциальная". Without is_won every pipeline reads as 0% realised.
WON_STAGE_NAMES = {
    'Контракт подписан', 'Программа продана', 'Спонсорство оформлено',
    'Программа завершена', 'Сдано', 'Проведено', 'Подписано',
    'Участие оформлено',
}


def _seed_crm_stages(env, teams):
    stages = {}
    for team_key, names in STAGES_BY_TEAM.items():
        stages[team_key] = {}
        for i, name in enumerate(names):
            stage = _ref(env, f'stage_{team_key}_{i}', 'crm.stage', {
                'name': name,
                'sequence': (i + 1) * 10,
                'team_ids': [(6, 0, [teams[team_key].id])],
                'is_won': name in WON_STAGE_NAMES,
            })
            stages[team_key][name] = stage
    return stages


def _seed_crm_tags(env):
    tags = {}
    for i, name in enumerate(TAGS):
        tags[name] = _ref(env, f'crm_tag_{i}', 'crm.tag', {'name': name})
    return tags


def _seed_crm_leads(env, partners, teams, stages, tags, users):
    for i, (name, partner_key, team_key, stage_name, revenue, prob, owner_key, priority, tag_names) in enumerate(LEADS):
        _ref(env, f'lead_{i}', 'crm.lead', {
            'name': name,
            'type': 'opportunity',
            'partner_id': partners[partner_key].id,
            'team_id': teams[team_key].id,
            'stage_id': stages[team_key][stage_name].id,
            'expected_revenue': revenue,
            'probability': prob,
            'user_id': users[owner_key].id,
            'priority': priority,
            'tag_ids': [(6, 0, [tags[t].id for t in tag_names])],
        })


# ---------------------------------------------------------------------------
# Projects & tasks
# ---------------------------------------------------------------------------

# key, name, owner_key, date_start, date (deadline), partner_key, description
PROJECTS = [
    ('proj_partnerships', 'Партнёрства и индустриальное взаимодействие 2026', 'kaiyrzhan', '2026-01-01', '2026-12-31', 'MAIN',
     'Флагманский проект корпоративных партнёрств: контракты R&D, лицензирование, визиты делегаций, совместные лаборатории.'),
    ('proj_internships', 'Стажировки — набор и распределение 2026', 'kaiyrzhan', '2026-02-01', '2026-12-15', None,
     'Воронка кандидатов на стажировку; клиент — студент, результат — трудоустройство, а не выручка.'),
    ('proj_academic', 'Академические партнёрства — меморандумы и обмены 2026', 'madi', '2026-01-10', '2026-12-31', None,
     'MoU с зарубежными университетами, программы мобильности и двойных дипломов.'),
    ('proj_sponsorship', 'Спонсорство и фандрайзинг 2026', 'anargul', '2026-01-15', '2026-12-31', None,
     'Спонсорство и благотворительность: именные стипендии, исследовательские гранты, спонсорство мероприятий.'),
    ('proj_training', 'Корпоративное обучение — программы 2026', 'madi', '2026-02-01', '2026-12-31', None,
     'Разработка и проведение программ корпоративного обучения.'),
    ('proj_consulting', 'Консалтинг и экспертные проекты 2026', 'kaiyrzhan', '2026-01-20', '2026-12-31', None,
     'Экспертные консалтинговые проекты для государственных и корпоративных клиентов.'),
    ('proj_events', 'Мероприятия и визиты 2026', 'anargul', '2026-01-01', '2026-12-31', None,
     'Деловые мероприятия, ярмарки вакансий, визиты делегаций, конференции.'),
    ('proj_accreditation', 'Аккредитация и институциональное развитие 2026', 'kaiyrzhan', '2026-01-05', '2026-12-20', None,
     'Подготовка к международной/национальной аккредитации, самообследование.'),
    ('proj_it', 'IT-инфраструктура кампуса — модернизация 2026', 'madi', '2026-03-01', '2026-12-31', None,
     'Внутренний IT-проект: модернизация сети/Wi-Fi/серверов (без внешнего партнёра).'),
    ('proj_admissions', 'Приёмная кампания 2026', 'anargul', '2026-01-10', '2026-08-31', None,
     'Внутренний проект маркетинга и операций приёмной кампании.'),
]

TASK_STAGES_BY_PROJECT = {
    'proj_partnerships': ['Новая заявка', 'В работе', 'На согласовании', 'Завершено'],
    'proj_internships': ['CV получено', 'Скрининг', 'Собеседование', 'Согласовано с компанией', 'Оформлено', 'Отказ'],
    'proj_academic': ['Инициировано', 'Переговоры', 'Юридическая проверка', 'Подписание', 'Реализация'],
    'proj_sponsorship': ['Заявка', 'Оценка', 'Согласование', 'Подписано', 'Устойчивость'],
    'proj_training': ['Запрос', 'Разработка программы', 'Согласование', 'Проведение', 'Обратная связь'],
    'proj_consulting': ['Запрос', 'Скоуп и предложение', 'Исполнение', 'Сдача результатов', 'Закрыт'],
    'proj_events': ['Планирование', 'Подготовка', 'Проведение', 'Итоги'],
    'proj_accreditation': ['Самообследование', 'Подготовка отчёта', 'Внешняя проверка', 'Решение'],
    'proj_it': ['Планирование', 'Закупка', 'Внедрение', 'Тестирование', 'Завершено'],
    'proj_admissions': ['Стратегия', 'Контент и реклама', 'Мероприятия для абитуриентов', 'Приём заявок', 'Зачисление'],
}

# project_key, name, stage_name, partner_key, deadline, assignee_key, priority, [subtask names]
TASKS = [
    # proj_partnerships
    ('proj_partnerships', 'Организовать визит делегации Tengizchevroil в кампус', 'Завершено', 'tco', '2026-08-10', 'kaiyrzhan', '1', []),
    ('proj_partnerships', 'Согласовать лицензионное соглашение — КазАтомПром', 'Завершено', 'kazatomprom', '2026-07-15', 'kaiyrzhan', '2', []),
    ('proj_partnerships', 'Подготовить программу Data Science — Halyk Bank', 'Новая заявка', 'halyk', '2026-09-10', 'kaiyrzhan', '1', []),
    ('proj_partnerships', 'Оформить договор R&D — КазМунайГаз (катализатор нефтепереработки)', 'Завершено', 'kmg', '2026-08-20', 'kaiyrzhan', '2', []),
    ('proj_partnerships', 'Настроить программу стажировок — EY Казахстан', 'В работе', 'ey_kz', '2026-09-20', 'kaiyrzhan', '1', []),
    ('proj_partnerships', 'Подготовить материалы Career Fair NU 2026 — Air Astana', 'На согласовании', 'air_astana', '2026-09-05', 'kaiyrzhan', '1', []),
    ('proj_partnerships', 'Организовать Industry Day 2026 с ERG', 'Новая заявка', 'erg', '2026-09-20', 'madi', '1',
     ['Согласовать программу мероприятия с ERG', 'Забронировать площадку и оборудование']),
    ('proj_partnerships', 'Подготовить NDA — ERG (совместная лаборатория геологоразведки)', 'В работе', 'erg', '2026-08-28', 'madi', '2',
     ['Согласовать текст NDA с юридическим отделом', 'Получить подпись от ERG']),

    # proj_internships
    ('proj_internships', 'Когорта IT-стажировок — Halyk Bank (5 мест)', 'Согласовано с компанией', 'halyk', '2026-09-10', 'kaiyrzhan', '1', []),
    ('proj_internships', 'Когорта стажировок — Теңізшевройл (разведка и добыча, 4 места)', 'CV получено', 'tco', '2026-10-15', 'kaiyrzhan', '1', []),
    ('proj_internships', 'Кандидат: А. Жумабекова — интервью', 'Согласовано с компанией', 'halyk', '2026-09-05', 'kaiyrzhan', '1',
     ['Провести техническое интервью', 'Собрать обратную связь от Halyk Bank']),
    ('proj_internships', 'Кандидат: Н. Сериков — интервью', 'Согласовано с компанией', 'halyk', '2026-09-06', 'kaiyrzhan', '1', []),
    ('proj_internships', 'Когорта стажировок — EY Казахстан (аудит, 3 места)', 'Собеседование', 'ey_kz', '2026-09-20', 'madi', '1', []),
    ('proj_internships', 'Когорта стажировок — Air Astana (наземные службы, 6 мест)', 'Скрининг', 'air_astana', '2026-10-01', 'anargul', '1', []),
    ('proj_internships', 'Кандидат отозвал заявку — Beeline', 'Отказ', 'beeline', '2026-07-20', 'anargul', '0', []),
    ('proj_internships', 'Когорта стажировок — ERG (совместная лаборатория, 2 места)', 'Оформлено', 'erg', '2026-08-01', 'madi', '1',
     ['Оформить пропуска на территорию ERG', 'Провести инструктаж по технике безопасности']),
    ('proj_internships', 'Кандидат: С. Ахметова — скрининг резюме', 'Собеседование', 'ey_kz', '2026-09-12', 'madi', '1', []),

    # proj_academic
    ('proj_academic', 'Юридическая проверка соглашения с University of Melbourne', 'Юридическая проверка', None, '2026-09-05', 'kaiyrzhan', '2', []),
    ('proj_academic', 'MoU с University of Cambridge — обмен студентами', 'Переговоры', None, '2026-09-30', 'madi', '2',
     ['Согласовать текст MoU с юридическим отделом', 'Назначить дату видеозвонка для подписания']),
    ('proj_academic', 'Продление соглашения с TU Munich', 'Подписание', None, '2026-08-25', 'madi', '1', []),
    ('proj_academic', 'MoU с Seoul National University — двойной диплом (Engineering)', 'Инициировано', None, '2026-10-20', 'anargul', '1', []),
    ('proj_academic', 'Летняя школа 2026 совместно с KAIST', 'Реализация', None, '2026-07-01', 'anargul', '1', []),

    # proj_sponsorship
    ('proj_sponsorship', 'Именная стипендия — Kaspi.kz (10 стипендий/год)', 'Подписано', 'kaspi', '2026-09-01', 'anargul', '1', []),
    ('proj_sponsorship', 'Спонсорская поддержка Career Fair — BI Group', 'Согласование', 'bi_group', '2026-09-15', 'madi', '1', []),
    ('proj_sponsorship', 'Спонсорство исследовательского гранта — Samsung', 'Оценка', 'samsung', '2026-10-05', 'kaiyrzhan', '1', []),
    ('proj_sponsorship', 'Заявка на спонсорство от Самрук-Қазына', 'Заявка', 'samruk', '2026-11-01', 'anargul', '1', []),
    ('proj_sponsorship', 'Годовой отчёт спонсорам — Казахтелеком', 'Устойчивость', 'kazakhtelecom', '2026-06-30', 'kaiyrzhan', '0', []),

    # proj_training
    ('proj_training', 'Программа Data Science для сотрудников — Halyk Bank', 'Проведение', 'halyk', '2026-09-10', 'madi', '2', []),
    ('proj_training', 'Executive-программа для менеджеров — КазАтомПром', 'Согласование', 'kazatomprom', '2026-09-25', 'anargul', '1', []),
    ('proj_training', 'Курс по МСФО — KPMG Казахстан', 'Разработка программы', 'kpmg_kz', '2026-10-01', 'kaiyrzhan', '1', []),
    ('proj_training', 'Запрос на обучение по кибербезопасности — Beeline', 'Запрос', 'beeline', '2026-11-05', 'madi', '1', []),
    ('proj_training', 'Обратная связь по программе — Baker Hughes', 'Обратная связь', 'baker_hughes', '2026-07-15', 'kaiyrzhan', '0', []),

    # proj_consulting
    ('proj_consulting', 'Экспертиза энергоперехода — Самрук-Қазына', 'Исполнение', 'samruk', '2026-09-30', 'kaiyrzhan', '1', []),
    ('proj_consulting', 'Сдача отчёта — КазМунайГаз (нефтепереработка)', 'Сдача результатов', 'kmg', '2026-08-30', 'madi', '2', []),
    ('proj_consulting', 'Логистическая экспертиза — KTZ', 'Запрос', 'ktz', '2026-11-10', 'kaiyrzhan', '1', []),
    ('proj_consulting', 'Консультации по цифровизации сети — Казахтелеком', 'Скоуп и предложение', 'kazakhtelecom', '2026-10-15', 'anargul', '1', []),
    ('proj_consulting', 'Проект закрыт — BI Group (аудит процессов)', 'Закрыт', 'bi_group', '2026-06-15', 'anargul', '0', []),
    ('proj_consulting', 'Сбор данных по возобновляемой энергетике', 'Исполнение', 'samruk', '2026-09-10', 'kaiyrzhan', '1',
     ['Собрать данные от полевых инженеров', 'Провести первичный анализ данных']),
    ('proj_consulting', 'Черновик аналитического отчёта', 'Исполнение', 'samruk', '2026-09-20', 'madi', '1', []),

    # proj_events
    ('proj_events', 'Дни открытых дверей — регионы Казахстана', 'Планирование', None, '2026-04-20', 'kaiyrzhan', '1', []),
    ('proj_events', 'Career Fair NU 2026 — материалы и логистика', 'Проведение', None, '2026-09-12', 'anargul', '1', []),
    ('proj_events', 'Ярмарка вакансий и набор выпускников — Air Astana', 'Проведение', 'air_astana', '2026-09-05', 'anargul', '1', []),
    ('proj_events', 'Industry Day 2026 с ERG — подготовка', 'Подготовка', 'erg', '2026-09-20', 'madi', '1', []),
    ('proj_events', 'Визит делегации Baker Hughes в кампус', 'Планирование', 'baker_hughes', '2026-10-10', 'kaiyrzhan', '1',
     ['Составить программу визита', 'Согласовать пропуска для делегации']),

    # proj_accreditation
    ('proj_accreditation', 'Самообследование программы Computer Science (ABET)', 'Подготовка отчёта', None, '2026-09-01', 'kaiyrzhan', '2', []),
    ('proj_accreditation', 'Визит внешних экспертов — School of Engineering', 'Внешняя проверка', None, '2026-11-20', 'anargul', '1',
     ['Подготовить помещения и материалы для экспертов', 'Согласовать расписание встреч с деканами']),
    ('proj_accreditation', 'Подготовка отчёта для национальной аккредитации (НААР)', 'Самообследование', None, '2026-10-15', 'madi', '1', []),
    ('proj_accreditation', 'Решение по аккредитации программы MBA (получено)', 'Решение', None, '2026-05-01', 'kaiyrzhan', '1', []),

    # proj_it
    ('proj_it', 'Закупка серверного оборудования (тендер)', 'Закупка', None, '2026-10-01', 'kaiyrzhan', '1', []),
    ('proj_it', 'Техническое задание на модернизацию Wi-Fi в общежитиях', 'Планирование', None, '2026-09-15', 'madi', '1', []),
    ('proj_it', 'Внедрение новой сети в корпусе Engineering', 'Внедрение', None, '2026-11-01', 'anargul', '1',
     ['Проложить магистральный кабель', 'Настроить коммутаторы уровня доступа']),
    ('proj_it', 'Нагрузочное тестирование сети библиотеки', 'Тестирование', None, '2026-11-20', 'kaiyrzhan', '1', []),
    ('proj_it', 'Прокладка кабельной сети — 3 этаж', 'Внедрение', None, '2026-10-20', 'anargul', '1', []),
    ('proj_it', 'Настройка точек доступа Wi-Fi', 'Внедрение', None, '2026-10-25', 'madi', '1', []),
    ('proj_it', 'test', 'Планирование', None, None, None, '0', []),

    # proj_admissions
    ('proj_admissions', 'Дни открытых дверей — регионы Казахстана', 'Мероприятия для абитуриентов', None, '2026-04-20', 'kaiyrzhan', '1', []),
    ('proj_admissions', 'Приём заявок абитуриентов', 'Приём заявок', None, '2026-07-01', 'anargul', '1', []),
    ('proj_admissions', 'Стратегия приёмной кампании 2026', 'Стратегия', None, '2026-02-01', 'anargul', '1', []),
    ('proj_admissions', 'Рекламная кампания в соцсетях', 'Контент и реклама', None, '2026-03-15', 'madi', '1', []),
    ('proj_admissions', 'Зачисление студентов 2026 года — завершено', 'Зачисление', None, '2026-08-25', 'madi', '1', []),
]


def _seed_projects(env, users, partners, company):
    projects = {}
    for key, name, owner_key, date_start, date_end, partner_key, description in PROJECTS:
        vals = {
            'name': name,
            'user_id': users[owner_key].id,
            'date_start': date_start,
            'date': date_end,
            'description': description,
        }
        if partner_key == 'MAIN':
            vals['partner_id'] = company.partner_id.id
        elif partner_key:
            vals['partner_id'] = partners[partner_key].id
        projects[key] = _ref(env, key, 'project.project', vals)
    return projects


def _seed_task_stages(env, projects):
    stages = {}
    for proj_key, names in TASK_STAGES_BY_PROJECT.items():
        stages[proj_key] = {}
        for i, name in enumerate(names):
            stage = _ref(env, f'taskstage_{proj_key}_{i}', 'project.task.type', {
                'name': name,
                'sequence': (i + 1) * 10,
                'project_ids': [(6, 0, [projects[proj_key].id])],
            })
            stages[proj_key][name] = stage
    return stages


def _seed_tasks(env, projects, task_stages, partners, users):
    for i, (proj_key, name, stage_name, partner_key, deadline, assignee_key, priority, subtasks) in enumerate(TASKS):
        vals = {
            'name': name,
            'project_id': projects[proj_key].id,
            'stage_id': task_stages[proj_key][stage_name].id,
            'priority': priority,
        }
        if partner_key:
            vals['partner_id'] = partners[partner_key].id
        if deadline:
            vals['date_deadline'] = deadline + ' 17:00:00'
        if assignee_key:
            vals['user_ids'] = [(6, 0, [users[assignee_key].id])]
        task = _ref(env, f'task_{i}', 'project.task', vals)

        for j, subtask_name in enumerate(subtasks):
            sub_vals = {
                'name': subtask_name,
                'project_id': projects[proj_key].id,
                'parent_id': task.id,
                'priority': priority,
            }
            if assignee_key:
                sub_vals['user_ids'] = [(6, 0, [users[assignee_key].id])]
            _ref(env, f'task_{i}_sub_{j}', 'project.task', sub_vals)


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------

# name, start, stop, partner_key_or_None
EVENTS = [
    ('Переговоры по совместной лаборатории — ERG', '2026-08-24 09:00:00', '2026-08-24 10:00:00', 'erg'),
    ('Do sports', '2026-08-20 14:00:00', '2026-08-20 16:00:00', None),
    ('Визит делегации Tengizchevroil в кампус NU', '2026-08-10 05:00:00', '2026-08-10 08:00:00', 'tco'),
    ('Демо-звонок: программа Data Science — Halyk Bank', '2026-08-26 06:00:00', '2026-08-26 07:00:00', 'halyk'),
    ('Подписание NDA — ERG', '2026-08-28 07:00:00', '2026-08-28 07:30:00', 'erg'),
    ('Координация Career Fair NU 2026 — Air Astana', '2026-09-05 05:00:00', '2026-09-05 06:00:00', 'air_astana'),
    ('Встреча с Kaspi.kz — именная стипендия', '2026-09-01 08:00:00', '2026-09-01 09:00:00', 'kaspi'),
    ('Технический совет — модернизация Wi-Fi кампуса', '2026-09-15 06:00:00', '2026-09-15 07:00:00', None),
    ('Industry Day 2026 — совместно с ERG', '2026-09-15 04:00:00', '2026-09-15 12:00:00', 'erg'),
    ('Kickoff консалтингового проекта — Самрук-Қазына', '2026-09-10 07:00:00', '2026-09-10 08:30:00', 'samruk'),
    ('Подписание MoU — University of Cambridge (видеозвонок)', '2026-09-30 09:00:00', '2026-09-30 10:00:00', None),
    ('Визит внешних экспертов по аккредитации — School of Engineering', '2026-11-20 05:00:00', '2026-11-20 12:00:00', None),
    ('Дни открытых дверей для абитуриентов — Алматы', '2026-04-20 04:00:00', '2026-04-20 11:00:00', None),
]


def _seed_calendar_events(env, partners):
    for i, (name, start, stop, partner_key) in enumerate(EVENTS):
        vals = {'name': name, 'start': start, 'stop': stop}
        if partner_key:
            partner = partners[partner_key]
            attendee_ids = partner.child_ids[:1].ids or [partner.id]
            vals['partner_ids'] = [(6, 0, attendee_ids)]
        _ref(env, f'event_{i}', 'calendar.event', vals)


# ---------------------------------------------------------------------------
# Surveys
# ---------------------------------------------------------------------------

SURVEYS = [
    ('survey_partner', 'Опрос удовлетворённости партнёров NU', [
        ('Насколько вы удовлетворены сотрудничеством с NU?', 'simple_choice', ['Очень доволен', 'Доволен', 'Нейтрально', 'Не доволен']),
        ('Что можно улучшить в процессе взаимодействия?', 'text_box', []),
        ('Порекомендуете ли вы сотрудничество с NU другим компаниям?', 'simple_choice', ['Да', 'Нет', 'Возможно']),
    ]),
    ('survey_intern', 'Обратная связь от стажёров 2026', [
        ('Как вы оцениваете свою стажировку в целом?', 'simple_choice', ['Отлично', 'Хорошо', 'Удовлетворительно', 'Плохо']),
        ('Стажировка соответствовала описанию вакансии?', 'simple_choice', ['Да', 'Нет', 'Частично']),
        ('Что могло бы сделать программу лучше?', 'text_box', []),
        ('Порекомендуете ли вы эту стажировку другим студентам?', 'simple_choice', ['Да', 'Нет', 'Возможно']),
    ]),
]


def _seed_surveys(env):
    for key, title, questions in SURVEYS:
        survey = _ref(env, key, 'survey.survey', {'title': title})
        for i, (qtitle, qtype, answers) in enumerate(questions):
            q_vals = {
                'title': qtitle,
                'question_type': qtype,
                'survey_id': survey.id,
                'sequence': i + 1,
            }
            if answers:
                try:
                    q_vals['suggested_answer_ids'] = [(0, 0, {'value': a}) for a in answers]
                except Exception:
                    _logger.warning("nu_demo_seed_data: could not set answer options for %s", qtitle)
            _ref(env, f'{key}_q{i}', 'survey.question', q_vals)


# ---------------------------------------------------------------------------
# Public events (event.event) — reuses names already established via CRM
# leads / calendar events, so the same story shows up consistently across apps.
# Requires the 'event' app; not declared as a hard manifest dependency since
# it's optional polish, not core to the dataset — guarded with a try/except.
# ---------------------------------------------------------------------------

EVENTS_APP = [
    ('event_career_fair', 'Career Fair NU 2026', '2026-09-12 10:00:00', '2026-09-12 18:00:00', 'Booked'),
    ('event_industry_day', 'Industry Day 2026 совместно с ERG', '2026-09-15 09:00:00', '2026-09-15 17:00:00', 'Announced'),
    ('event_startup_weekend', 'Startup Weekend NU', '2026-11-01 13:00:00', '2026-11-03 18:00:00', 'New'),
]


def _seed_public_events(env):
    if 'event.event' not in env:
        return
    stages = {s.name: s.id for s in env['event.stage'].search([])}
    for key, name, date_begin, date_end, stage_name in EVENTS_APP:
        _ref(env, key, 'event.event', {
            'name': name,
            'date_begin': date_begin,
            'date_end': date_end,
            'stage_id': stages.get(stage_name),
        })
