from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_cyber_lab_key'
DB_FILE = 'alif_lab.db'
UPLOAD_FOLDER = 'static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# RBAC Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor for all templates
@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
    return dict(current_user=user)

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    participants = conn.execute('SELECT * FROM users WHERE role = "participant" ORDER BY points DESC').fetchall()
    conn.close()
    return render_template('dashboard.html', participants=participants)

@app.route('/playground/red')
@login_required
def red_team():
    return render_template('red_team.html')

@app.route('/playground/blue')
@login_required
def blue_team():
    return render_template('blue_team.html')

@app.route('/playground/purple')
@login_required
def purple_team():
    return render_template('purple_team.html')

@app.route('/playground/sqli', methods=('GET', 'POST'))
@login_required
def sqli_lab():
    message = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # INTENTIONAL SQL INJECTION VULNERABILITY
        conn = get_db_connection()
        # Vulnerable query
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            user = conn.execute(query).fetchone()
            if user:
                return redirect(url_for('sqli_success'))
            else:
                message = "Login failed."
        except sqlite3.Error as e:
            message = f"Database Error: {e}"
        finally:
            conn.close()

    return render_template('sqli_lab.html', message=message)

@app.route('/playground/sqli/success')
@login_required
def sqli_success():
    return render_template('sqli_success.html')

@app.route('/playground/red/xss', methods=['GET', 'POST'])
@login_required
def xss_lab():
    search_query = request.form.get('query', '') if request.method == 'POST' else request.args.get('query', '')
    
    # INTENTIONAL XSS VULNERABILITY: 
    # We will pass this to the template and use the |safe filter in Jinja to prevent escaping.
    
    return render_template('xss_lab.html', search_query=search_query)

@app.route('/ctf')
@login_required
def ctf():
    return render_template('ctf.html')

# --- Alif Finance CTF Challenge (IDOR) ---
@app.route('/ctf/alif_finance')
@login_required
def alif_finance():
    # Pass a default user_id (e.g. 3) to the balance checking URL
    return render_template('alif_finance_dashboard.html')

@app.route('/ctf/alif_finance/balance')
@login_required
def alif_finance_balance():
    # The vulnerability: Taking user_id directly from the URL without checking ownership
    target_user_id = request.args.get('user_id', '3')
    
    # Simulate DB records for the challenge
    if target_user_id == '1':
        # Admin / Target Account -> Shows the Flag
        account_data = {
            'name': 'CEO Alif Finance',
            'balance': 'Rp 99.999.999.999',
            'address': 'Jl. Rahasia Negara No. 1, Jakarta (Super Secret Vault)',
            'flag': 'ALIF{yahh_ketahuan}'
        }
    elif target_user_id == '2':
        # Random other user -> No flag
        account_data = {
            'name': 'Bapak Fulan',
            'balance': 'Rp 1.500.000',
            'address': 'Jl. Kenangan No. 42, Bandung',
            'flag': None
        }
    elif target_user_id == '3':
        # The participant's supposed account -> No flag
        account_data = {
            'name': 'Participant (Anda)',
            'balance': 'Rp 5.000.000',
            'address': 'Jl. Belajar Cyber No. 99',
            'flag': None
        }
    else:
        # Unknown user
        account_data = {
            'name': 'Unknown User',
            'balance': 'Rp 0',
            'address': 'Unknown',
            'flag': None
        }
        
    return render_template('alif_finance_balance.html', account=account_data, user_id=target_user_id)

@app.route('/blog')
@login_required
def blog():
    conn = get_db_connection()
    # Fetch all posts with their authors
    posts = conn.execute('SELECT blogs.*, users.username FROM blogs JOIN users ON blogs.author_id = users.id ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('blog.html', posts=posts)

@app.route('/blog/create', methods=('GET', 'POST'))
@login_required
def create_blog():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form.get('category', 'Blue Team')
        
        if title and content:
            conn = get_db_connection()
            conn.execute('INSERT INTO blogs (title, content, category, author_id) VALUES (?, ?, ?, ?)', 
                         (title, content, category, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('blog'))
            
    return render_template('create_blog.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '')
        school = request.form.get('school', '')
        address = request.form.get('address', '')
        bio = request.form.get('bio', '')
        
        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_picture = filename

        conn = get_db_connection()
        if profile_picture:
            conn.execute('''
                UPDATE users 
                SET full_name = ?, school = ?, address = ?, bio = ?, profile_picture = ?
                WHERE id = ?
            ''', (full_name, school, address, bio, profile_picture, session['user_id']))
        else:
            conn.execute('''
                UPDATE users 
                SET full_name = ?, school = ?, address = ?, bio = ?
                WHERE id = ?
            ''', (full_name, school, address, bio, session['user_id']))
            
        conn.commit()
        conn.close()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
        
    return render_template('profile.html')

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

# API Routes for Chat
@app.route('/api/chat/public', methods=['GET'])
@login_required
def get_public_chat():
    conn = get_db_connection()
    messages = conn.execute('''
        SELECT chat_messages.*, users.username 
        FROM chat_messages 
        JOIN users ON chat_messages.sender_id = users.id 
        WHERE receiver_id IS NULL 
        ORDER BY timestamp ASC
    ''').fetchall()
    conn.close()
    return jsonify([dict(m) for m in messages])

@app.route('/api/chat/public', methods=['POST'])
@login_required
def post_public_chat():
    content = request.json.get('content')
    if content:
        conn = get_db_connection()
        conn.execute('INSERT INTO chat_messages (sender_id, content) VALUES (?, ?)', (session['user_id'], content))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.route('/api/chat/request', methods=['POST'])
@login_required
def request_chat():
    unique_id = request.json.get('unique_id')
    conn = get_db_connection()
    target_user = conn.execute('SELECT id FROM users WHERE unique_id = ?', (unique_id,)).fetchone()
    
    if target_user:
        target_id = target_user['id']
        if target_id == session['user_id']:
             conn.close()
             return jsonify({'status': 'error', 'message': 'Cannot chat with yourself'})
             
        # Check if already requested or accepted
        existing = conn.execute('SELECT * FROM chat_requests WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)',
                                (session['user_id'], target_id, target_id, session['user_id'])).fetchone()
        
        if not existing:
            conn.execute('INSERT INTO chat_requests (sender_id, receiver_id) VALUES (?, ?)', (session['user_id'], target_id))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success', 'message': 'Chat request sent!'})
        else:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Request already exists'})
            
    conn.close()
    return jsonify({'status': 'error', 'message': 'User not found'})

@app.route('/api/chat/requests/incoming', methods=['GET'])
@login_required
def get_chat_requests():
    conn = get_db_connection()
    requests = conn.execute('''
        SELECT chat_requests.id, users.username, users.unique_id, chat_requests.status 
        FROM chat_requests 
        JOIN users ON chat_requests.sender_id = users.id 
        WHERE receiver_id = ? AND status = 'pending'
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in requests])

@app.route('/api/chat/request/handle', methods=['POST'])
@login_required
def handle_chat_request():
    req_id = request.json.get('request_id')
    action = request.json.get('action') # 'accept' or 'decline'
    
    conn = get_db_connection()
    req = conn.execute('SELECT * FROM chat_requests WHERE id = ? AND receiver_id = ?', (req_id, session['user_id'])).fetchone()
    
    if req:
        if action == 'accept':
            conn.execute('UPDATE chat_requests SET status = "accepted" WHERE id = ?', (req_id,))
        else:
            conn.execute('DELETE FROM chat_requests WHERE id = ?', (req_id,))
        conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/chat/private/contacts', methods=['GET'])
@login_required
def get_private_contacts():
    conn = get_db_connection()
    # Get all users we have an accepted chat request with
    contacts = conn.execute('''
        SELECT users.id, users.username, users.unique_id
        FROM users
        JOIN chat_requests ON 
            (chat_requests.sender_id = users.id AND chat_requests.receiver_id = ? AND chat_requests.status = 'accepted')
            OR
            (chat_requests.receiver_id = users.id AND chat_requests.sender_id = ? AND chat_requests.status = 'accepted')
    ''', (session['user_id'], session['user_id'])).fetchall()
    conn.close()
    return jsonify([dict(c) for c in contacts])

@app.route('/api/chat/private/<int:contact_id>', methods=['GET'])
@login_required
def get_private_chat(contact_id):
    conn = get_db_connection()
    messages = conn.execute('''
        SELECT chat_messages.*, users.username 
        FROM chat_messages 
        JOIN users ON chat_messages.sender_id = users.id 
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    ''', (session['user_id'], contact_id, contact_id, session['user_id'])).fetchall()
    conn.close()
    return jsonify([dict(m) for m in messages])

@app.route('/api/chat/private/<int:contact_id>', methods=['POST'])
@login_required
def post_private_chat(contact_id):
    content = request.json.get('content')
    if content:
        conn = get_db_connection()
        conn.execute('INSERT INTO chat_messages (sender_id, receiver_id, content) VALUES (?, ?, ?)', 
                     (session['user_id'], contact_id, content))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
