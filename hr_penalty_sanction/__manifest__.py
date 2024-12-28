{
    'name': 'HR Penal Sanctions',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Manage penal sanctions, stages, and violations for employees.',
    'author': 'Einas Omer',
    'depends': ['hr','hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_sanction_views.xml',
        'views/hr_penal_category_views.xml',
        'views/hr_penal_stage_views.xml',
        'views/hr_penal_violation_views.xml',
        'views/hr_department_views.xml',
        'data/hr_payslip_rules.xml',
        'data/sequence.xml',
        'data/hr_penalty_notification_email_template.xml',
        'reports/hr_penalty_notification_report.xml',
    ],
    'installable': True,
    'application': True,
}

