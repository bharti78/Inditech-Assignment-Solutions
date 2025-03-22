# User Portal

This is a Django-based user portal application that provides user authentication, customer management, and webhook notifications.

## Features
- User authentication (Login, Logout, Registration)
- Customer management (CRUD operations)
- Webhook notifications for customer actions
- Admin panel for managing users and customers

## Installation Guide

### Prerequisites
- Python 3.x installed
- Virtual environment (optional but recommended)

### Setup Instructions

1. Clone the repository:
   ```sh
   git clone <your-repo-url>
   cd user_portal
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```sh
   python manage.py migrate
   ```

5. Create a superuser:
   ```sh
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```sh
   python manage.py runserver
   ```

7. Open the browser and navigate to `http://127.0.0.1:8000/`

## Environment Variables

Ensure you have a `.env` file set up with necessary configurations. You can refer to `.env.example` for required variables.

## Dependencies

The project requires the following dependencies:
```
Django==4.2.10
django-allauth==0.61.1
django-crispy-forms==2.1
crispy-bootstrap5==2023.10
xhtml2pdf==0.2.13
requests==2.31.0
python-dotenv==1.0.1
```
3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

## Contributing
Feel free to fork this repository and contribute!

## License
This project is licensed under the MIT License.
