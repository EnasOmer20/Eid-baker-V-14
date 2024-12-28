{
    'name': 'HR Attendance Enhancements',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Enhance HR Attendance with late, overtime calculations and approval workflow',
    'description': """
        - Adds holiday hours and working hours fields to contracts.
        - Tracks late and overtime hours in attendance records.
        - Adds approval buttons for deductions and overtime in attendance logs.
        - Automatically calculates payslip rules for deductions and overtime.
    """,
    'author': 'Einas Omer',
    'depends': ['hr', 'hr_payroll', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payslip_rules.xml',
        'views/hr_contract_views.xml',
        'views/hr_attendance_views.xml',
        'wizards/employee_late_overtime_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
