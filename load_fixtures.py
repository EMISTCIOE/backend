import os

os.system("python manage.py loaddata user_role")
os.system("python manage.py loaddata dummy_users")
os.system("python manage.py loaddata fiscal_session_bs")
os.system("python manage.py loaddata category")
