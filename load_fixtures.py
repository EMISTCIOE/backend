# ruff: noqa
import os

os.system("python manage.py loaddata main_module")
os.system("python manage.py loaddata permission_category")
os.system("python manage.py loaddata permissions")
os.system("python manage.py loaddata user_role")
os.system("python manage.py loaddata fiscal_session_bs")
os.system("python manage.py loaddata notice_category")
os.system("python manage.py loaddata campus_info")
