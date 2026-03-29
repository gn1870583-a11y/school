from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'academic-success-secret-key-2026'
CORS(app, supports_credentials=True)

# Database
users = {}
study_plans = []
messages = []
mental_health_records = []
warnings = []

# ==================== PAGE ROUTES ====================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/selector')
def selector():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('selector.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return redirect(url_for('selector'))

# ==================== DASHBOARD NAVIGATION ====================

@app.route('/dashboard/student')
def student_dashboard_view():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    session['role'] = 'student'
    return render_template('student_dashboard.html')

@app.route('/dashboard/lecturer')
def lecturer_dashboard_view():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    session['role'] = 'lecturer'
    return render_template('lecturer_dashboard.html')

@app.route('/dashboard/mentor')
def mentor_dashboard_view():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    session['role'] = 'mentor'
    return render_template('mentor_dashboard.html')

@app.route('/dashboard/admin')
def admin_dashboard_view():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    session['role'] = 'admin'
    return render_template('admin_dashboard.html')

# ==================== API ROUTES ====================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = users.get(username)
    if user and check_password_hash(user['password'], password):
        session['username'] = username
        session['name'] = user['name']
        session['role'] = user['role']
        session['user_id'] = user['id']
        return jsonify({'success': True, 'message': 'Login successful', 'name': user['name'], 'role': user['role']})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    if username in users:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    new_id = len(users) + 1
    users[username] = {
        'id': new_id,
        'username': username,
        'password': generate_password_hash(data.get('password')),
        'name': data.get('name'),
        'email': data.get('email'),
        'role': data.get('role', 'student')
    }
    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/current-user')
def current_user():
    if 'username' not in session:
        return jsonify({'logged_in': False}), 401
    return jsonify({
        'logged_in': True,
        'username': session.get('username'),
        'name': session.get('name'),
        'role': session.get('role')
    })

# ==================== STUDENT APIs ====================

@app.route('/api/student/dashboard')
def student_dashboard():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({
        'student': {'name': session.get('name')},
        'performance': {'gpa': 3.4, 'attendance_avg': 88, 'courses_completed': 4},
        'courses': [
            {'code': 'CS101', 'name': 'Programming Fundamentals', 'grade': 'B+', 'attendance': 85},
            {'code': 'MATH201', 'name': 'Calculus II', 'grade': 'C+', 'attendance': 70},
            {'code': 'ENG102', 'name': 'English Composition', 'grade': 'A-', 'attendance': 95},
            {'code': 'PHY101', 'name': 'Physics', 'grade': 'B', 'attendance': 78}
        ]
    })

@app.route('/api/student/study-plan', methods=['GET', 'POST'])
def student_study_plan():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    user_id = session.get('user_id')
    if request.method == 'GET':
        return jsonify([p for p in study_plans if p.get('user_id') == user_id])
    data = request.get_json()
    new_plan = {
        'id': len(study_plans) + 1,
        'user_id': user_id,
        'title': data.get('title'),
        'description': data.get('description'),
        'date': data.get('date'),
        'completed': False
    }
    study_plans.append(new_plan)
    return jsonify(new_plan), 201

@app.route('/api/student/mental-health', methods=['GET', 'POST'])
def mental_health():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    user_id = session.get('user_id')
    if request.method == 'GET':
        return jsonify([r for r in mental_health_records if r.get('user_id') == user_id])
    data = request.get_json()
    new_record = {
        'id': len(mental_health_records) + 1,
        'user_id': user_id,
        'stress': data.get('stress'),
        'sleep': data.get('sleep'),
        'anxiety': data.get('anxiety'),
        'date': datetime.now().isoformat()
    }
    mental_health_records.append(new_record)
    return jsonify(new_record), 201

# ==================== MENTOR APIs ====================

@app.route('/api/mentor/messages', methods=['GET', 'POST'])
def mentor_messages():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    user_id = session.get('user_id')
    if request.method == 'GET':
        return jsonify([m for m in messages if m.get('receiver_id') == user_id or m.get('sender_id') == user_id])
    data = request.get_json()
    new_msg = {
        'id': len(messages) + 1,
        'sender_id': user_id,
        'receiver_id': data.get('receiver_id'),
        'content': data.get('content'),
        'timestamp': datetime.now().isoformat()
    }
    messages.append(new_msg)
    return jsonify(new_msg), 201

@app.route('/api/mentor/mentees')
def mentor_mentees():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    mentees = []
    for user in users.values():
        if user.get('role') == 'student':
            mentees.append({
                'id': user['id'],
                'name': user['name'],
                'student_id': f"STU{user['id']:04d}",
                'gpa': 3.0 + (user['id'] * 0.05),
                'department': ['Computer Science', 'Business', 'Engineering'][user['id'] % 3]
            })
    return jsonify(mentees[:5])

# ==================== LECTURER APIs ====================

@app.route('/api/lecturer/students')
def lecturer_students():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    students_list = []
    for user in users.values():
        if user.get('role') == 'student':
            gpa = 2.8 + (user['id'] * 0.1)
            students_list.append({
                'id': user['id'],
                'name': user['name'],
                'student_id': f"STU{user['id']:04d}",
                'gpa': round(gpa, 2),
                'attendance_avg': 75 + (user['id'] * 5),
                'status': 'At Risk' if gpa < 2.5 else 'Good'
            })
    return jsonify(students_list)

@app.route('/api/lecturer/early-warning', methods=['POST'])
def lecturer_early_warning():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    warnings.append({
        'student': data.get('student_name'),
        'type': data.get('warning_type'),
        'message': data.get('message'),
        'date': datetime.now().isoformat()
    })
    return jsonify({'success': True})

# ==================== ADMIN APIs ====================

@app.route('/api/admin/analytics')
def admin_analytics():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    students = [u for u in users.values() if u.get('role') == 'student']
    return jsonify({
        'total_students': len(students),
        'average_gpa': 3.2,
        'students_at_risk': 2,
        'retention_rate': 94.8,
        'departments': {'Computer Science': 2, 'Business': 1, 'Engineering': 1}
    })

# ==================== DEMO USERS ====================
demo_users = {
    'student1': {'id': 1, 'name': 'Alex Johnson', 'role': 'student', 'password': 'student123'},
    'student2': {'id': 2, 'name': 'Emma Wilson', 'role': 'student', 'password': 'student123'},
    'lecturer1': {'id': 3, 'name': 'Dr. Sarah Chen', 'role': 'lecturer', 'password': 'lecturer123'},
    'mentor1': {'id': 4, 'name': 'Prof. Michael Brown', 'role': 'mentor', 'password': 'mentor123'},
    'admin1': {'id': 5, 'name': 'Admin User', 'role': 'admin', 'password': 'admin123'}
}

for username, data in demo_users.items():
    users[username] = {
        'id': data['id'],
        'username': username,
        'password': generate_password_hash(data['password']),
        'name': data['name'],
        'email': f"{username}@university.edu",
        'role': data['role']
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)
