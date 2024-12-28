
{
    'name': 'Visa Expiration Alert',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Manage visa expiration alerts for employees.',
    'author': 'Einas Omer',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/visa_expiration_issue_views.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
}
