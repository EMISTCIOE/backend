# Thapathali Campus EMIS BACKEND

##  Quick Start with uv (Recommended)

This project uses [uv](https://github.com/astral-sh/uv) - an extremely fast Python package manager and virtual environment tool.

### Prerequisites

Install uv if you haven't already:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Setup

1. **Navigate to the project directory and run the setup script:**

   ```bash
   ./scripts/uv_setup.sh
   ```

   This will:
   - Create a virtual environment in `.venv`
   - Install all dependencies from `pyproject.toml`

2. **Activate the virtual environment:**

   ```bash
   source .venv/bin/activate
   ```

3. **Apply database migrations:**

   ```bash
   uv run python manage.py migrate
   ```

4. **Create a superuser account:**

   ```bash
   uv run python manage.py createsuperuser
   ```

5. **Load fixtures:**

   ```bash
   uv run python load_fixtures.py
   ```

6. **Load static files:**

   ```bash
   uv run python manage.py collectstatic
   ```

7. **Start the Django server:**

   ```bash
   uv run python manage.py runserver
   ```

###  Managing Dependencies with uv

**Add a new package:**
```bash
uv add package-name
# or use the helper script:
./scripts/uv_add.sh package-name
# or use make:
make add PACKAGE=package-name
```

**Sync dependencies after pulling changes:**
```bash
uv sync
# or use the helper script:
./scripts/uv_sync.sh
# or use make:
make sync
```

## Environment variables

The backend loads secrets from `.env` and other environment files. The email reset automation
requires a single value:

- `EMAIL_RESET_WEBHOOK_URL`: public webhook URL exposed by your n8n workflow.

**Run any command in the uv environment:**
```bash
uv run <command>
# or use the helper script:
./scripts/uv_run.sh python manage.py <command>
```

### � Pip Protection

This project has **pip protection** enabled to prevent accidental use of pip commands. If you try to use `pip install`, you'll see an error message with the correct `uv` command to use instead.

**Why?** Using `uv` ensures:
- Faster dependency resolution and installation
- Consistent lock file (`uv.lock`) for reproducible builds
- Better dependency management across the team

**If you accidentally try to use pip:**
```bash
$ pip install some-package
  ERROR: Direct pip usage is disabled in this project!

Instead of pip commands, use:
  pip install <package>    →  uv add <package>
  pip install -r ...       →  uv sync
  pip uninstall <package>  →  uv remove <package>
```

**Emergency bypass** (not recommended):
```bash
.venv/bin/pip.real install <package>
```

###  Makefile Commands

For convenience, you can use the included Makefile:

```bash
make help          # Show all available commands
make setup         # Setup project with uv
make run           # Run development server
make migrate       # Run database migrations
make shell         # Open Django shell
make test          # Run tests
make lint          # Run linting
make format        # Format code
make fixtures      # Load fixtures
make superuser     # Create superuser
```

---

##  Alternative Setup (Traditional Method)

If you prefer using traditional `pip` and `venv`:

1. Navigate to the project directory and create a virtual environment by running: - python -m venv venv

   2. Activate the virtual environment by running the command:

      - source venv/bin/activate
        OR - .\venv\Scripts\activate

   3. Install the required dependencies by running the command:

      - pip install -r requirements.txt
      - pre-commit install

   4. Next, apply the database migrations by running:

      - python manage.py migrate

   5. Create a superuser account by running:

      - python manage.py createsuperuser

   6. Load Fixtures:

      - python load_fixtures.py

   7. Load the static files

      - python manage.py collectstatic

   8. Finally, start the Django server by running:
      - python manage.py runserver

---

##  Formatting and Linting Code

1. ruff check / ruff check --fix / ruff format
2. black .
3. pre-commit run --all-files

# Contributing to Project

Remember, Good PR makes you a Good contributor !

We work hard to maintain the structure, and [use conventional Pull](https://github.com/emis-tcioe/tcioe-emis/blob/main/CONTRIBUTING.md#pull-request-title-format-) request titles and commits. Without a proper template for the PR, not following the guidelines and spam might get the pull request closed, or banned.

- [Contributing Guidelines](/CONTRIBUTING.md) to be followed.
