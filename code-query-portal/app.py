import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from flask_session import Session  # Added for better session management
from functools import wraps
from werkzeug.utils import secure_filename

# Load environment variables from .env file
load_dotenv(verbose=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Debug print statements for OAuth configuration
print("==== OAuth Debug Information ====")
print(f"GOOGLE_CLIENT_ID exists: {'Yes' if os.environ.get('GOOGLE_CLIENT_ID') else 'No'}")
print(f"GOOGLE_CLIENT_SECRET exists: {'Yes' if os.environ.get('GOOGLE_CLIENT_SECRET') else 'No'}")
print(f"Redirect URI: http://localhost:5000/login/google/callback")
print("================================")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or 'dev-secret-key-for-testing-only'  # Use consistent secret key

# Enhanced session configuration to fix CSRF state issues
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Initialize Flask-Session
Session(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///code_query_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# OAuth Configuration - Updated for better compatibility and state handling
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={
        'scope': 'email profile',
        'redirect_uri': 'http://localhost:5000/login/google/callback',
        'token_endpoint_auth_method': 'client_secret_post'
    }
)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    queries = db.relationship('Query', backref='user', lazy=True)

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    query_text = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    matched = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_now():
    return {'now': datetime.now()}
# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/login/google')
def login_google():
    # Clear any existing session data
    session.clear()
    
    # Generate and store a new state parameter
    state = os.urandom(16).hex()
    session['oauth_state'] = state
    
    redirect_uri = url_for('google_auth', _external=True)
    print(f"Redirecting to Google with redirect_uri: {redirect_uri}")
    return google.authorize_redirect(redirect_uri, state=state)

@app.route('/login/google/callback')
def google_auth():
    try:
        # Verify state parameter
        expected_state = session.pop('oauth_state', None)
        token = google.authorize_access_token()
        
        # Get user info
        resp = google.get('userinfo')
        user_info = resp.json()
        
        # Print debug info
        print(f"User info received: {user_info.get('email')}")
        
        # Check if user exists
        user = User.query.filter_by(email=user_info['email']).first()
        
        if not user:
            # Create new user
            user = User(
                email=user_info['email'],
                name=user_info.get('name'),
                profile_pic=user_info.get('picture')
            )
            db.session.add(user)
            db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        return redirect(url_for('index'))
    except Exception as e:
        print(f"OAuth error: {str(e)}")
        flash(f"Authentication error: {str(e)}", "danger")
        return redirect(url_for('login'))

# Temporary bypass login for testing
@app.route('/bypass-login')
def bypass_login():
    # Create a test user
    email = "test@example.com"
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name="Test User")
        db.session.add(user)
        db.session.commit()
    
    # Set session
    session['user_id'] = user.id
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/query', methods=['POST'])
@login_required
def process_query():
    user_id = session['user_id']
    query_text = request.form.get('query', '')
    
    if not query_text:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    # Log the query
    logger.info(f"User {user_id} submitted query: {query_text}")
    
    # Find matching solution
    solution = find_solution(query_text)
    
    # Save query to database
    query = Query(
        user_id=user_id,
        query_text=query_text,
        response=solution['code'] if solution['found'] else "No response.",
        matched=solution['found']
    )
    db.session.add(query)
    db.session.commit()
    
    # Add query_id to the response
    solution['query_id'] = query.id
    
    return jsonify(solution)

@app.route('/history')
@login_required
def history():
    user_id = session['user_id']
    queries = Query.query.filter_by(user_id=user_id).order_by(Query.timestamp.desc()).all()
    return render_template('history.html', queries=queries)

@app.route('/download/<int:query_id>')
@login_required
def download_solution(query_id):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from io import BytesIO
    
    query = Query.query.get_or_404(query_id)
    
    # Check if user owns this query
    if query.user_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('history'))
    
    # Create PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add content to PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "Code Query Solution")
    
    c.setFont("Helvetica", 12)
    c.drawString(72, height - 100, f"Query: {query.query_text}")
    c.drawString(72, height - 120, f"Date: {query.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    c.setFont("Courier", 10)
    y_position = height - 150
    for i, line in enumerate(query.response.split('\n')):
        c.drawString(72, y_position - (i * 12), line)
    
    c.save()
    buffer.seek(0)
    
    # Create a filename
    filename = f"solution_{query_id}_{secure_filename(query.query_text[:20])}.pdf"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save the PDF
    with open(filepath, 'wb') as f:
        f.write(buffer.read())
    
    return redirect(url_for('view_pdf', filename=filename))

@app.route('/view/<filename>')
@login_required
def view_pdf(filename):
    return render_template('view_pdf.html', filename=filename)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def find_solution(query):
    """
    Find a matching solution in the solutions.txt file
    """
    try:
        with open('solutions.txt', 'r') as f:
            content = f.read()
        
        # Split the content by comment lines
        solutions = []
        current_comment = None
        current_code = []
        
        for line in content.split('\n'):
            if line.startswith('#'):
                # If we already have a comment, save the previous solution
                if current_comment:
                    solutions.append({
                        'comment': current_comment,
                        'code': '\n'.join(current_code).strip()
                    })
                # Start a new solution
                current_comment = line.strip()
                current_code = []
            elif current_comment:
                current_code.append(line)
        
        # Add the last solution if there is one
        if current_comment and current_code:
            solutions.append({
                'comment': current_comment,
                'code': '\n'.join(current_code).strip()
            })
        
        # Find a matching solution
        for solution in solutions:
            # Remove the # from the comment for comparison
            clean_comment = solution['comment'][1:].strip().lower()
            if clean_comment in query.lower() or query.lower() in clean_comment:
                return {
                    'found': True,
                    'comment': solution['comment'],
                    'code': solution['code']
                }
        
        return {
            'found': False,
            'comment': '',
            'code': 'No response.'
        }
    
    except Exception as e:
        logger.error(f"Error finding solution: {str(e)}")
        return {
            'found': False,
            'comment': '',
            'code': 'An error occurred while processing your query.'
        }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)