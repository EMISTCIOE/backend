# Thapathali Campus EMIS BACKEND


**To get started with the Project, follow these simple steps:**

1. Navigate to the project directory and create a virtual environment by running: - python -m venv venv

   2. Activate the virtual environment by running the command:

      - source venv/bin/activate
        OR - .\venv\Scripts\activate

   3. Install the required dependencies by running the command:

      - pip install -r requirements\base.txt
      - pre-commit install

   4. Next, apply the database migrations by running:

      - python manage.py migrate

   5. Create a superuser account by running:

      - python manage.py createsuperuser

   6. Load the static files

      - python manage.py collectstatic

   7. Finally, start the Django server by running:
      - python manage.py runserver

**Formatting and Linting Code**

1. ruff check / ruff check --fix / ruff format
2. black .
3. pre-commit run --all-files
