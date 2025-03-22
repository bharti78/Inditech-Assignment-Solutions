# Code Query Portal

A web-based platform that allows users to submit, manage, and resolve code-related queries efficiently.

## Features

- **User Authentication**: Secure login and registration system.
- **Query Submission**: Users can submit coding-related queries.
- **Query Management**: Track query status and manage responses.
- **Admin Panel**: Admins can review and respond to queries.
- **Webhook Integration**: Notifications for important events.
- **Database Management**: Uses PostgreSQL for data storage.
- **Responsive UI**: Fully responsive frontend.

## Installation Guide

### Prerequisites

Ensure you have the following installed on your system:

- **Python 3.8+**: [Download here](https://www.python.org/downloads/)
- **PostgreSQL**: [Download here](https://www.postgresql.org/download/)
- **Virtual Environment**: (Included in Python)
- **Git**: [Download here](https://git-scm.com/downloads)

### Step-by-Step Setup

1. **Clone the Repository**
   ```sh
   git clone <your-repository-url>
   cd code-query-portal
   ```

2. **Create a Virtual Environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # MacOS/Linux
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set Up Database**
   - Create a PostgreSQL database.
   - Configure database settings in `settings.py`:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'your_database_name',
             'USER': 'your_username',
             'PASSWORD': 'your_password',
             'HOST': 'localhost',
             'PORT': '5432',
         }
     }
     ```

5. **Run Migrations**
   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```sh
   python manage.py createsuperuser
   ```

7. **Run Server**
   ```sh
   python manage.py runserver
   ```

8. **Access Application**
   Open your browser and visit:
   ```
   http://127.0.0.1:8000/
   ```

## Dependencies

- **Django**
- **Django REST Framework**
- **PostgreSQL**
- **Celery (if using async tasks)**
- **Redis (if used for caching)**

## Environment Variables

Create a `.env` file and add:

```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/dbname
```

## Contributing

Feel free to submit pull requests or raise issues.

## License

This project is under the MIT License.
