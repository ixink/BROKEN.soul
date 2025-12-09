import json
import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'super_secure_key_change_in_prod'

DB_FILE = 'database.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"users": {}, "posts": []}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

os.makedirs('static/uploads', exist_ok=True)

@app.route('/')
def index():
    if 'student_id' in session:
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = load_db()
        sid = request.form['student_id'].strip()
        if sid in db['users']:
            flash('Student ID already taken.')
            return redirect(url_for('signup'))
        password = request.form['password'].encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        db['users'][sid] = {
            'name': request.form['name'],
            'dept': request.form['dept'],
            'phone': request.form['phone'],
            'email': request.form['email'],
            'password': hashed.decode('utf-8'),  # Store as string for JSON compatibility
            'role': 'Broken',
            'profile_pic': '/static/default_pic.jpg',
            'long_description': ''
        }
        save_db(db)
        flash('Welcome! You can now log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = load_db()
        sid = request.form['student_id']
        pwd = request.form['password'].encode('utf-8')
        user = db['users'].get(sid)
        if user and bcrypt.checkpw(pwd, user['password'].encode('utf-8')):
            session['student_id'] = sid
            return redirect(url_for('feed'))
        flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('student_id', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    db = load_db()
    user = db['users'][session['student_id']]
    if request.method == 'POST':
        user['role'] = request.form['role']
        user['long_description'] = request.form.get('long_description', '')
        if 'profile_pic' in request.files and request.files['profile_pic'].filename:
            file = request.files['profile_pic']
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
            filename = f"{session['student_id']}.{ext}"
            file.save(f"static/uploads/{filename}")
            user['profile_pic'] = f"/static/uploads/{filename}"
        save_db(db)
        flash('Profile updated.')
    return render_template('profile.html', user=user)

@app.route('/feed')
def feed():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    db = load_db()
    current_user = db['users'][session['student_id']]
    posts = db['posts'][::-1]
    return render_template('feed.html', posts=posts, users=db['users'], current_user=current_user)

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    db = load_db()
    db['posts'].append({
        'author_id': session['student_id'],
        'title': request.form['title'],
        'short_desc': request.form['short_desc'],
        'free_time': request.form.get('free_time', ''),
        'place': request.form.get('place', ''),
        'favorite': request.form.get('favorite', '')
    })
    save_db(db)
    flash('Your story has been shared.')
    return redirect(url_for('feed'))

@app.route('/delete_post/<int:post_index>', methods=['POST'])
def delete_post(post_index):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    db = load_db()
    if 0 <= post_index < len(db['posts']) and db['posts'][post_index]['author_id'] == session['student_id']:
        del db['posts'][post_index]
        save_db(db)
        flash('Story removed.')
    else:
        flash('Cannot delete this story.')
    return redirect(url_for('feed'))

@app.route('/message/<author_id>')
def message(author_id):
    db = load_db()
    author = db['users'].get(author_id)
    if not author:
        flash('User not found.')
        return redirect(url_for('feed'))
    return render_template('message.html', author=author)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

