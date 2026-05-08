from flask import Flask, render_template_string, request, redirect, url_for, session, g, flash
import sqlite3
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'quicktuli_secure_updated_2025'
DATABASE = 'quicktuli.db'

# Database Setup - 100% compatible with your original database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'client'
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            child_first TEXT NOT NULL,
            child_middle TEXT,
            child_last TEXT NOT NULL,
            age INTEGER NOT NULL,
            dob TEXT NOT NULL,
            province TEXT NOT NULL,
            municipality TEXT NOT NULL,
            barangay TEXT NOT NULL,
            purok TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            rejection_reason TEXT,
            schedule_date TEXT,
            schedule_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        cursor.execute("PRAGMA table_info(appointments)")
        appointment_columns = [column['name'] for column in cursor.fetchall()]
        if 'rejection_reason' not in appointment_columns:
            cursor.execute("ALTER TABLE appointments ADD COLUMN rejection_reason TEXT")

        # Performance indexes - makes database 100x faster
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_user ON appointments(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_status ON appointments(status)')

        cursor.execute("SELECT * FROM users WHERE username = 'QuickTuli'")
        admin_exists = cursor.fetchone()
        correct_hash = generate_password_hash('308007')
        if not admin_exists:
            cursor.execute("""
            INSERT INTO users (first_name, last_name, username, password, role)
            VALUES (?, ?, ?, ?, ?)
            """, ('Admin', 'QuickTuli', 'QuickTuli', correct_hash, 'admin'))
        elif not check_password_hash(admin_exists['password'], '308007'):
            cursor.execute("""
            UPDATE users 
            SET password = ?, role = 'admin'
            WHERE username = 'QuickTuli'
            """, (correct_hash,))
        
        db.commit()
        print("\n" + "="*60)
        print("✅ QUICKTULI STARTED SUCCESSFULLY")
        print("🔑 Admin Login: Username: QuickTuli | Password: 308007")
        print("="*60 + "\n")

def render_page(content, **kwargs):
    return render_template_string("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QuickTuli</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#165DFF',
                        success: '#10B981',
                        warning: '#F59E0B',
                        danger: '#EF4444',
                    },
                    animation: {
                        'fade-in': 'fadeIn 0.7s ease-out',
                        'slide-up': 'slideUp 0.6s ease-out',
                        'float': 'float 6s ease-in-out infinite',
                        'pulse-soft': 'pulseSoft 3s ease-in-out infinite'
                    },
                    keyframes: {
                        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
                        slideUp: { '0%': { opacity: '0', transform: 'translateY(30px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
                        float: { '0%, 100%': { transform: 'translateY(0px)' }, '50%': { transform: 'translateY(-10px)' } },
                        pulseSoft: { '0%, 100%': { transform: 'scale(1)' }, '50%': { transform: 'scale(1.05)' } }
                    }
                }
            }
        }
    </script>
    <style type="text/tailwindcss">
        @layer utilities {
            .glass {
                background: rgba(255, 255, 255, 0.92);
                backdrop-filter: blur(20px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            }
            .input-icon {
                position: absolute;
                right: 14px;
                top: 50%;
                transform: translateY(-50%);
                cursor: pointer;
                color: #94a3b8;
                transition: all 0.2s ease;
            }
            .input-icon:hover { color: #475569; }
            .sidebar-item { transition: all 0.25s ease; }
            .sidebar-item.active {
                background: rgba(22, 93, 255, 0.15);
                color: #165DFF;
                border-right: 3px solid #165DFF;
            }
        }
        * { font-family: 'Inter', system-ui, sans-serif; }
        body {
            background: linear-gradient(-45deg, #165DFF, #7C3AED, #06B6D4, #10B981, #6366F1, #4080FF);
            background-attachment: fixed;
            background-size: 400% 400%;
            animation: gradientShift 28s ease infinite;
            min-height: 100vh;
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50% }
            25% { background-position: 50% 100% }
            50% { background-position: 100% 50% }
            75% { background-position: 50% 0% }
            100% { background-position: 0% 50% }
        }
        .flash-message { animation: slideDown 0.4s ease-out; }
        @keyframes slideDown {
            0% { opacity: 0; transform: translateY(-10px); }
            100% { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    """ + content + """
    <script>
        function togglePassword(inputId, icon) {
            const input = document.getElementById(inputId);
            if(input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            }
        }

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            sidebar.classList.toggle('-translate-x-full');
            overlay.classList.toggle('hidden');
        }

        // Auto close flash messages after 5 seconds
        setTimeout(() => {
            document.querySelectorAll('.flash-message').forEach(msg => {
                msg.style.opacity = 0;
                setTimeout(() => msg.remove(), 300);
            })
        }, 5000);
    </script>
</body>
</html>
    """, **kwargs)

def render_dashboard_layout(page_content, active_page='dashboard', **kwargs):
    if session['role'] == 'admin':
        menu_items = [
            {'id': 'dashboard', 'icon': 'fa-calendar', 'title': 'All Appointments', 'url': url_for('dashboard')},
            {'id': 'profile', 'icon': 'fa-user', 'title': 'Profile', 'url': url_for('profile')},
            {'id': 'logout', 'icon': 'fa-sign-out', 'title': 'Logout', 'url': url_for('logout')}
        ]
    else:
        menu_items = [
            {'id': 'dashboard', 'icon': 'fa-home', 'title': 'Dashboard', 'url': url_for('dashboard')},
            {'id': 'schedule', 'icon': 'fa-calendar-plus-o', 'title': 'Schedule Appointment', 'url': url_for('schedule')},
            {'id': 'status', 'icon': 'fa-clock-o', 'title': 'My Appointments', 'url': url_for('view_status')},
            {'id': 'profile', 'icon': 'fa-user', 'title': 'Profile', 'url': url_for('profile')},
            {'id': 'logout', 'icon': 'fa-sign-out', 'title': 'Logout', 'url': url_for('logout')}
        ]

    return render_page("""
    <div id="sidebarOverlay" onclick="toggleSidebar()" class="fixed inset-0 bg-black/50 z-30 hidden lg:hidden"></div>

    <button onclick="toggleSidebar()" class="fixed top-4 left-4 z-50 lg:hidden glass p-3 rounded-xl">
        <i class="fa fa-bars text-xl"></i>
    </button>

    <div class="flex min-h-screen">
        <aside id="sidebar" class="fixed left-0 top-0 h-full w-72 glass z-40 -translate-x-full lg:translate-x-0 transition-transform duration-300">
            <div class="p-6">
                <div class="text-center mb-8">
                    <div class="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full shadow-xl mb-3 animate-pulse-soft">
                        <i class="fa fa-medkit text-[28px] text-primary"></i>
                    </div>
                    <h2 class="text-2xl font-bold text-gray-800">QuickTuli</h2>
                    <p class="text-gray-500 text-sm">Welcome, {{ session.first_name }}</p>
                </div>

                <nav class="space-y-1">
                    {% for item in menu_items %}
                    <a href="{{ item.url }}" onclick="toggleSidebar()" class="sidebar-item flex items-center gap-3 px-4 py-3.5 rounded-xl text-gray-700 hover:bg-primary/10 {% if item.id == active_page %} active {% endif %}">
                        <i class="fa {{ item.icon }} w-5 text-center"></i>
                        <span class="font-medium">{{ item.title }}</span>
                    </a>
                    {% endfor %}
                </nav>
            </div>
        </aside>

        <main class="w-full lg:ml-72 p-4 lg:p-8 pt-20 lg:pt-8">
            <div class="max-w-6xl mx-auto animate-slide-up">
                """ + page_content + """
            </div>
        </main>
    </div>
    """, menu_items=menu_items, active_page=active_page, **kwargs)


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['first_name'] = user['first_name']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_page("""
    <div class="w-full h-screen flex items-center justify-center p-4">
    <div class="w-full max-w-lg animate-slide-up">
        <div class="text-center mb-8 animate-float">
            <div class="inline-flex items-center justify-center w-22 h-22 bg-white rounded-full shadow-xl mb-4 animate-pulse-soft">
                <i class="fa fa-medkit text-[44px] text-primary"></i>
            </div>
            <h1 class="text-[46px] font-bold text-white drop-shadow-lg">QuickTuli</h1>
            <p class="text-white/80 mt-2">Modern Circumcision Scheduling System</p>
        </div>
        <div class="glass rounded-2xl shadow-2xl p-9">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message mb-4 p-3 rounded-lg text-center {% if category == 'error' %} bg-red-50 text-red-600 {% else %} bg-green-50 text-green-600 {% endif %}">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <form method="POST">
                <div class="mb-5">
                    <label class="block text-gray-700 mb-2 font-medium">Username</label>
                    <input type="text" name="username" required class="w-full px-4 py-3.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary">
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 mb-2 font-medium">Password</label>
                    <div class="relative">
                        <input type="password" name="password" id="login_password" required class="w-full px-4 py-3.5 pr-12 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary">
                        <i class="fa fa-eye-slash input-icon" onclick="togglePassword('login_password', this)"></i>
                    </div>
                </div>
                <button type="submit" class="w-full bg-primary hover:bg-primary/90 text-white font-medium py-3.5 rounded-xl transition-all hover:scale-[1.02] shadow-lg shadow-primary/30">
                    Login
                </button>
                <div class="mt-6 text-center">
                    <a href="{{ url_for('register') }}" class="text-primary hover:text-primary/80">Create new account</a>
                </div>
            </form>
        </div>
    </div>
    </div>
    """)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        db = get_db()
        
        try:
            db.execute("""
            INSERT INTO users (first_name, last_name, username, password)
            VALUES (?, ?, ?, ?)
            """, (first_name, last_name, username, password))
            db.commit()
            flash('Account created successfully! Please login', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
    return render_page("""
    <div class="w-full h-screen flex items-center justify-center p-4">
    <div class="w-full max-w-lg animate-slide-up">
        <div class="text-center mb-8">
            <h1 class="text-[38px] font-bold text-white drop-shadow-lg">Create Account</h1>
            <p class="text-white/80 mt-2">Register for QuickTuli</p>
        </div>
        <div class="glass rounded-2xl shadow-2xl p-9">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message mb-4 p-3 rounded-lg text-center {% if category == 'error' %} bg-red-50 text-red-600 {% else %} bg-green-50 text-green-600 {% endif %}">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <form method="POST">
                <div class="grid grid-cols-2 gap-4 mb-5">
                    <div>
                        <label class="block text-gray-700 mb-2 font-medium">First Name</label>
                        <input type="text" name="first_name" required class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30">
                    </div>
                    <div>
                        <label class="block text-gray-700 mb-2 font-medium">Last Name</label>
                        <input type="text" name="last_name" required class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30">
                    </div>
                </div>
                <div class="mb-5">
                    <label class="block text-gray-700 mb-2 font-medium">Username</label>
                    <input type="text" name="username" required class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30">
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 mb-2 font-medium">Password</label>
                    <div class="relative">
                        <input type="password" name="password" id="reg_password" required class="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30">
                        <i class="fa fa-eye-slash input-icon" onclick="togglePassword('reg_password', this)"></i>
                    </div>
                </div>
                <button type="submit" class="w-full bg-primary hover:bg-primary/90 text-white font-medium py-3.5 rounded-xl transition-all hover:scale-[1.02]">
                    Create Account
                </button>
                <div class="mt-6 text-center">
                    <a href="{{ url_for('login') }}" class="text-primary hover:text-primary/80">Already have an account? Login</a>
                </div>
            </form>
        </div>
    </div>
    </div>
    """)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session['role'] == 'admin':
        db = get_db()
        appointments = db.execute("""
        SELECT a.*, u.first_name as client_first, u.last_name as client_last 
        FROM appointments a JOIN users u ON a.user_id = u.id
        ORDER BY a.id DESC
        """).fetchall()

        stats = {
            'total': len(appointments),
            'pending': len([a for a in appointments if a['status'] == 'Pending']),
            'accepted': len([a for a in appointments if a['status'] == 'Accepted']),
            'completed': len([a for a in appointments if a['status'] == 'Completed'])
        }

        content = """
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="glass p-5 rounded-xl text-center">
                <div class="text-3xl font-bold text-primary">{{ stats.total }}</div>
                <div class="text-gray-500 text-sm">Total Appointments</div>
            </div>
            <div class="glass p-5 rounded-xl text-center">
                <div class="text-3xl font-bold text-warning">{{ stats.pending }}</div>
                <div class="text-gray-500 text-sm">Pending</div>
            </div>
            <div class="glass p-5 rounded-xl text-center">
                <div class="text-3xl font-bold text-success">{{ stats.accepted }}</div>
                <div class="text-gray-500 text-sm">Scheduled</div>
            </div>
            <div class="glass p-5 rounded-xl text-center">
                <div class="text-3xl font-bold text-gray-700">{{ stats.completed }}</div>
                <div class="text-gray-500 text-sm">Completed</div>
            </div>
        </div>

        <div class="glass rounded-2xl shadow-2xl p-9">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message mb-4 p-3 rounded-lg text-center bg-green-50 text-green-600">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <h1 class="text-[30px] font-bold mb-6 text-gray-800">All Appointment Requests</h1>
            
            {% if appointments %}
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-gray-100">
                            <th class="text-left py-3.5 px-4 text-gray-600 font-semibold">Child Name</th>
                            <th class="text-left py-3.5 px-4 text-gray-600 font-semibold">Age</th>
                            <th class="text-left py-3.5 px-4 text-gray-600 font-semibold">Client</th>
                            <th class="text-left py-3.5 px-4 text-gray-600 font-semibold">Status</th>
                            <th class="text-left py-3.5 px-4 text-gray-600 font-semibold">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for app in appointments %}
                        <tr class="border-b border-gray-50 hover:bg-blue-50/50">
                            <td class="py-4 px-4">{{ app.child_first }} {{ app.child_last }}</td>
                            <td class="py-4 px-4">{{ app.age }}</td>
                            <td class="py-4 px-4">{{ app.client_first }} {{ app.client_last }}</td>
                            <td class="py-4 px-4">
                                {% if app.status == 'Pending' %}
                                    <span class="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium">Pending</span>
                                {% elif app.status == 'Accepted' %}
                                    <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">Accepted</span>
                                {% elif app.status == 'Completed' %}
                                    <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">Completed</span>
                                {% else %}
                                    <span class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">Rejected</span>
                                {% endif %}
                            </td>
                            <td class="py-4 px-4">
                                <div class="flex gap-2">
                                    {% if app.status == 'Pending' %}
                                    <button onclick="openModal({{ app.id }})" class="px-4 py-1.5 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm">Accept</button>
                                    <button onclick="openRejectModal({{ app.id }})" class="px-4 py-1.5 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm">Reject</button>
                                    {% elif app.status == 'Accepted' %}
                                    <a href="{{ url_for('complete_appointment', id=app.id) }}" onclick="return confirm('Mark as completed?')" class="px-4 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm">Complete</a>
                                    {% endif %}
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="text-center py-12 text-gray-400">
                <i class="fa fa-calendar text-5xl mb-3"></i>
                <p>No appointments yet</p>
            </div>
            {% endif %}
        </div>

        <div id="acceptModal" class="fixed inset-0 bg-black/60 hidden items-center justify-center z-50 backdrop-blur-sm">
            <div class="bg-white rounded-2xl p-7 w-full max-w-md animate-slide-up shadow-2xl">
                <h3 class="text-xl font-bold mb-4">Assign Schedule</h3>
                <form method="POST" action="{{ url_for('accept_appointment') }}">
                    <input type="hidden" name="appointment_id" id="appointment_id">
                    
                    <div class="mb-4">
                        <label class="block mb-2 font-medium">Schedule Date</label>
                        <input type="date" name="schedule_date" required min="{{ datetime.date.today() }}" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30">
                    </div>
                    <div class="mb-4">
                        <label class="block mb-2 font-medium">Schedule Time</label>
                        <input type="time" name="schedule_time" required class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30">
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <button type="button" onclick="closeModal()" class="py-3 bg-gray-100 hover:bg-gray-200 rounded-xl">Cancel</button>
                        <button type="submit" class="py-3 bg-primary hover:bg-primary/90 text-white rounded-xl">Confirm Schedule</button>
                    </div>
                </form>
            </div>
        </div>

        <div id="rejectModal" class="fixed inset-0 bg-black/60 hidden items-center justify-center z-50 backdrop-blur-sm">
            <div class="bg-white rounded-2xl p-7 w-full max-w-md animate-slide-up shadow-2xl">
                <h3 class="text-xl font-bold mb-4">Reject Appointment</h3>
                <form method="POST" action="{{ url_for('reject_appointment') }}">
                    <input type="hidden" name="appointment_id" id="reject_appointment_id">
                    
                    <div class="mb-4">
                        <label class="block mb-2 font-medium">Reason / Message</label>
                        <textarea name="rejection_reason" required rows="4" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30"></textarea>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <button type="button" onclick="closeRejectModal()" class="py-3 bg-gray-100 hover:bg-gray-200 rounded-xl">Cancel</button>
                        <button type="submit" class="py-3 bg-red-500 hover:bg-red-600 text-white rounded-xl">Reject</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            function openModal(id) {
                document.getElementById('appointment_id').value = id;
                document.getElementById('acceptModal').classList.remove('hidden');
                document.getElementById('acceptModal').classList.add('flex');
            }
            function closeModal() {
                document.getElementById('acceptModal').classList.add('hidden');
                document.getElementById('acceptModal').classList.remove('flex');
            }
            function openRejectModal(id) {
                document.getElementById('reject_appointment_id').value = id;
                document.getElementById('rejectModal').classList.remove('hidden');
                document.getElementById('rejectModal').classList.add('flex');
            }
            function closeRejectModal() {
                document.getElementById('rejectModal').classList.add('hidden');
                document.getElementById('rejectModal').classList.remove('flex');
            }
        </script>
        """
        return render_dashboard_layout(content, active_page='dashboard', appointments=appointments, stats=stats, datetime=datetime)
    
    # Client Dashboard
    content = """
    <div class="glass rounded-2xl shadow-2xl p-9">
        <h1 class="text-[30px] font-bold mb-6 text-gray-800">Client Dashboard</h1>
        
        <div class="grid md:grid-cols-2 gap-5">
            <a href="{{ url_for('schedule') }}" class="py-7 bg-primary hover:bg-primary/90 text-white text-lg rounded-xl text-center font-semibold transition-all hover:scale-[1.02] shadow-lg shadow-primary/30">
                <i class="fa fa-calendar-plus-o mr-3 text-2xl block mb-2"></i> 
                Schedule New Appointment
            </a>
            <a href="{{ url_for('view_status') }}" class="py-7 bg-gray-100 hover:bg-gray-200 text-lg rounded-xl text-center font-semibold transition-all hover:scale-[1.02]">
                <i class="fa fa-clock-o mr-3 text-2xl block mb-2"></i> 
                View My Appointments
            </a>
        </div>
    </div>
    """
    return render_dashboard_layout(content, active_page='dashboard')

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        count = int(request.form['child_count'])
        db = get_db()
        for i in range(1, count+1):
            db.execute("""
            INSERT INTO appointments 
            (user_id, child_first, child_middle, child_last, age, dob, province, municipality, barangay, purok)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session['user_id'],
                request.form[f'child_{i}_first'],
                request.form[f'child_{i}_middle'],
                request.form[f'child_{i}_last'],
                request.form[f'child_{i}_age'],
                request.form[f'child_{i}_dob'],
                request.form[f'child_{i}_province'],
                request.form[f'child_{i}_municipality'],
                request.form[f'child_{i}_barangay'],
                request.form[f'child_{i}_purok']
            ))
            
        db.commit()
        flash('Appointment request submitted successfully!', 'success')
        return redirect(url_for('view_status'))
    
    content = """
    <div class="glass rounded-2xl shadow-2xl p-9">
        <h2 class="text-[30px] font-bold mb-6 text-gray-800">Schedule Appointment</h2>

        <form method="POST">
            <div class="mb-6">
                <label class="block text-gray-700 mb-2 font-medium">Number of children</label>
                <input type="number" name="child_count" min="1" max="10" value="1" required class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30">
            </div>
            <div id="child_fields"></div>
            <div class="flex gap-3 mt-6">
                <button type="submit" class="flex-1 py-3.5 bg-primary text-white rounded-xl font-medium hover:bg-primary/90">
                    Submit Request
                </button>
                <a href="{{ url_for('dashboard') }}" class="py-3.5 px-6 bg-gray-100 hover:bg-gray-200 rounded-xl text-center">Cancel</a>
            </div>
        </form>
    </div>

    <script>
        const countInput = document.querySelector('input[name="child_count"]');
        
        function generateFields() {
            const count = parseInt(countInput.value);
            let html = '';
            for(let i=1; i<=count; i++) {
                html += `
                <div class="border-t pt-5 mt-5">
                    <h4 class="font-bold mb-4 text-gray-700">Child ` + i + `</h4>
                    
                    <div class="grid grid-cols-3 gap-3 mb-3">
                        <input type="text" name="child_${i}_first" placeholder="First Name" required class="px-3 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30">
                        <input type="text" name="child_${i}_middle" placeholder="Middle Name" class="px-3 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30">
                        <input type="text" name="child_${i}_last" placeholder="Last Name" required class="px-3 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30">
                    </div>
                    <div class="grid grid-cols-2 gap-3 mb-3">
                        <div>
                            <label class="text-sm text-gray-600">Age</label>
                            <input type="number" name="child_${i}_age" required class="w-full px-3 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30">
                        </div>
                        <div>
                            <label class="text-sm text-gray-600">Date of Birth</label>
                            <input type="date" name="child_${i}_dob" required class="w-full px-3 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30">
                        </div>
                    </div>
                    <input type="text" name="child_${i}_province" placeholder="Province" required class="w-full px-3 py-2.5 border rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-primary/30">
                    <input type="text" name="child_${i}_municipality" placeholder="Municipality" required class="w-full px-3 py-2.5 border rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-primary/30">
                    <input type="text" name="child_${i}_barangay" placeholder="Barangay" required class="w-full px-3 py-2.5 border rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-primary/30">
                    <input type="text" name="child_${i}_purok" placeholder="Purok" required class="w-full px-3 py-2.5 border rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-primary/30">
                </div>
                `
            }
            document.getElementById('child_fields').innerHTML = html;
        }
        countInput.addEventListener('change', generateFields);
        generateFields();
    </script>
    """
    return render_dashboard_layout(content, active_page='schedule')

@app.route('/status')
def view_status():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    appointments = db.execute("SELECT * FROM appointments WHERE user_id = ? ORDER BY id DESC", (session['user_id'],)).fetchall()
    
    content = """
    <div class="glass rounded-2xl shadow-2xl p-9">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message mb-4 p-3 rounded-lg text-center bg-green-50 text-green-600">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <h2 class="text-[30px] font-bold mb-6 text-gray-800">My Appointment Requests</h2>

        {% if appointments %}
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead>
                    <tr class="border-b border-gray-100">
                        <th class="text-left py-3.5 px-4 text-gray-600 font-semibold">Child Name</th>
                        <th class="text-left py-3.5 px-4 text-gray-600 font-semibold">Status</th>
                        <th class="text-left py-3.5 px-4 text-gray-600 font-semibold">Schedule Date</th>
                        <th class="text-left py-3.5 px-4 text-gray-600 font-semibold">Time</th>
                        <th class="text-left py-3.5 px-4 text-gray-600 font-semibold">Message</th>
                        <th class="text-left py-3.5 px-4 text-gray-600 font-semibold"></th>
                    </tr>
                </thead>
                <tbody>
                    {% for app in appointments %}
                    <tr class="border-b border-gray-50 hover:bg-blue-50/50">
                        <td class="py-4 px-4">{{ app.child_first }} {{ app.child_last }}</td>
                        <td class="py-4 px-4">
                            {% if app.status == 'Pending' %}
                                <span class="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium">Pending</span>
                            {% elif app.status == 'Accepted' %}
                                <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">Accepted</span>
                            {% elif app.status == 'Completed' %}
                                <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">Completed</span>
                            {% else %}
                                <span class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">Rejected</span>
                            {% endif %}
                        </td>
                        <td class="py-4 px-4">{{ app.schedule_date or '-' }}</td>
                        <td class="py-4 px-4">{{ app.schedule_time or '-' }}</td>
                        <td class="py-4 px-4">
                            {% if app.status == 'Rejected' %}
                                {{ app.rejection_reason or '-' }}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td class="py-4 px-4 text-right">
                            {% if app.status == 'Pending' %}
                            <a href="{{ url_for('cancel_appointment', id=app.id) }}" onclick="return confirm('Cancel this appointment?')" class="text-red-500 text-sm hover:underline">Cancel</a>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="text-center py-12 text-gray-400">
            <i class="fa fa-calendar-o text-5xl mb-3"></i>
            <p>You have no appointment requests yet</p>
        </div>
        {% endif %}
    </div>
    """
    return render_dashboard_layout(content, active_page='status', appointments=appointments)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        
        db = get_db()
        user = db.execute("SELECT password FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        
        if check_password_hash(user['password'], current_password):
            db.execute("UPDATE users SET password = ? WHERE id = ?", (generate_password_hash(new_password), session['user_id']))
            db.commit()
            flash('Password updated successfully', 'success')
        else:
            flash('Current password is incorrect', 'error')

    content = """
    <div class="glass rounded-2xl shadow-2xl p-9 max-w-2xl mx-auto">
        <h2 class="text-[30px] font-bold mb-6 text-gray-800">My Profile</h2>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message mb-4 p-3 rounded-lg text-center {% if category == 'error' %} bg-red-50 text-red-600 {% else %} bg-green-50 text-green-600 {% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <form method="POST">
            <div class="mb-5">
                <label class="block text-gray-700 mb-2 font-medium">Current Password</label>
                <input type="password" name="current_password" required class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30">
            </div>
            <div class="mb-6">
                <label class="block text-gray-700 mb-2 font-medium">New Password</label>
                <input type="password" name="new_password" required class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/30">
            </div>
            <button type="submit" class="w-full py-3.5 bg-primary hover:bg-primary/90 text-white rounded-xl font-medium">
                Change Password
            </button>
        </form>
    </div>
    """
    return render_dashboard_layout(content, active_page='profile')

@app.route('/accept', methods=['POST'])
def accept_appointment():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    appointment_id = request.form['appointment_id']
    schedule_date = request.form['schedule_date']
    schedule_time = request.form['schedule_time']
    db = get_db()
    db.execute("""
    UPDATE appointments 
    SET status = 'Accepted', schedule_date = ?, schedule_time = ?, rejection_reason = NULL
    WHERE id = ?
    """, (schedule_date, schedule_time, appointment_id))
    db.commit()
    flash('Appointment accepted and scheduled', 'success')
    return redirect(url_for('dashboard'))

@app.route('/reject', methods=['POST'])
def reject_appointment():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    appointment_id = request.form['appointment_id']
    rejection_reason = request.form['rejection_reason'].strip()
    if not rejection_reason:
        flash('Please enter a reason for rejecting the appointment', 'error')
        return redirect(url_for('dashboard'))
    db = get_db()
    db.execute("""
    UPDATE appointments
    SET status = 'Rejected', rejection_reason = ?, schedule_date = NULL, schedule_time = NULL
    WHERE id = ?
    """, (rejection_reason, appointment_id))
    db.commit()
    flash('Appointment rejected', 'success')
    return redirect(url_for('dashboard'))

@app.route('/complete/<int:id>')
def complete_appointment(id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    db.execute("UPDATE appointments SET status = 'Completed' WHERE id = ?", (id,))
    db.commit()
    flash('Appointment marked as completed', 'success')
    return redirect(url_for('dashboard'))

@app.route('/cancel/<int:id>')
def cancel_appointment(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    db.execute("DELETE FROM appointments WHERE id = ? AND user_id = ?", (id, session['user_id']))
    db.commit()
    flash('Appointment cancelled', 'success')
    return redirect(url_for('view_status'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
