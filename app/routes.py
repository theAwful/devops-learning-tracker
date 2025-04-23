from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user, login_user, logout_user
import bleach
import bcrypt
from datetime import datetime, date
from app import db
from app.models import User, UserInfo, Resource, Goal, Project, Progress

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@login_required
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            if not Progress.query.filter_by(user_id=user.id).first():
                progress = Progress(user_id=user.id, total_points=0, milestone='Beginner')
                db.session.add(progress)
                db.session.commit()
            return redirect(url_for('main.index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(username=username, password=hashed.decode('utf-8'))
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error='Registration failed: ' + str(e))
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/api/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    progress = Progress.query.filter_by(user_id=current_user.id).first()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'progress': {
            'total_points': progress.total_points,
            'milestone': progress.milestone,
            'last_checkin': str(progress.last_checkin) if progress.last_checkin else None
        },
        'goals': [{'title': g.title, 'category': g.category} for g in goals],
        'today': str(date.today())
    })

@main.route('/api/checkin', methods=['POST'])
@login_required
def api_checkin():
    progress = Progress.query.filter_by(user_id=current_user.id).first()
    today = date.today()
    if progress.last_checkin != today:
        progress.total_points += 5
        progress.last_checkin = today
        if progress.total_points >= 200:
            progress.milestone = 'Pro'
        elif progress.total_points >= 100:
            progress.milestone = 'Novice'
        db.session.commit()
    return jsonify({'success': True})

@main.route('/api/resources', methods=['GET', 'POST'])
@login_required
def api_resources():
    if request.method == 'POST':
        title = bleach.clean(request.form['title'])
        url = bleach.clean(request.form['url'])
        notes = bleach.clean(request.form['notes'])
        category = bleach.clean(request.form['category'])
        tags = bleach.clean(request.form['tags'])
        resource = Resource(title=title, url=url, notes=notes, category=category, tags=tags, user_id=current_user.id)
        db.session.add(resource)
        db.session.commit()
        return jsonify({'success': True})
    resources = Resource.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'resources': [{
            'title': r.title,
            'url': r.url,
            'notes': r.notes,
            'category': r.category,
            'tags': r.tags
        } for r in resources]
    })

@main.route('/api/goals', methods=['GET', 'POST'])
@login_required
def api_goals():
    if request.method == 'POST':
        title = bleach.clean(request.form['title'])
        deadline = request.form['deadline']
        points = int(request.form['points'])
        category = bleach.clean(request.form['category'])
        deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date() if deadline else None
        goal = Goal(title=title, deadline=deadline_date, points=points, category=category, user_id=current_user.id)
        db.session.add(goal)
        db.session.commit()
        return jsonify({'success': True})
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'goals': [{
            'title': g.title,
            'deadline': str(g.deadline) if g.deadline else None,
            'points': g.points,
            'status': g.status,
            'category': g.category
        } for g in goals]
    })

@main.route('/api/projects', methods=['GET', 'POST'])
@login_required
def api_projects():
    if request.method == 'POST':
        title = bleach.clean(request.form['title'])
        description = bleach.clean(request.form['description'])
        repo_url = bleach.clean(request.form['repo_url'])
        notes = bleach.clean(request.form['notes'])
        points = int(request.form['points'])
        project = Project(title=title, description=description, repo_url=repo_url, notes=notes, points=points, user_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        return jsonify({'success': True})
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'projects': [{
            'title': p.title,
            'description': p.description,
            'repo_url': p.repo_url,
            'notes': p.notes,
            'points': p.points,
            'completed': p.completed
        } for p in projects]
    })

@main.route('/api/export', methods=['GET'])
@login_required
def api_export():
    resources = Resource.query.filter_by(user_id=current_user.id).all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'resources': [{'title': r.title, 'url': r.url, 'notes': r.notes, 'category': r.category, 'tags': r.tags} for r in resources],
        'goals': [{'title': g.title, 'deadline': str(g.deadline) if g.deadline else None, 'progress': g.progress, 'points': g.points, 'status': g.status, 'category': g.category} for g in goals],
        'projects': [{'title': p.title, 'description': p.description, 'repo_url': p.repo_url, 'notes': p.notes, 'points': p.points, 'completed': p.completed} for p in projects]
    })

@main.route('/api/import', methods=['POST'])
@login_required
def api_import():
    data = request.get_json()
    for r in data.get('resources', []):
        resource = Resource(title=bleach.clean(r['title']), url=bleach.clean(r['url']), notes=bleach.clean(r['notes']), category=bleach.clean(r['category']), tags=bleach.clean(r['tags']), user_id=current_user.id)
        db.session.add(resource)
    for g in data.get('goals', []):
        deadline = datetime.strptime(g['deadline'], '%Y-%m-%d').date() if g.get('deadline') else None
        goal = Goal(title=bleach.clean(g['title']), deadline=deadline, progress=g['progress'], points=g['points'], status=bleach.clean(g['status']), category=bleach.clean(g['category']), user_id=current_user.id)
        db.session.add(goal)
    for p in data.get('projects', []):
        project = Project(title=bleach.clean(p['title']), description=bleach.clean(p['description']), repo_url=bleach.clean(p['repo_url']), notes=bleach.clean(p['notes']), points=p['points'], completed=p['completed'], user_id=current_user.id)
        db.session.add(project)
    db.session.commit()
    return jsonify({'success': True})

@main.route('/api/account', methods=['GET'])
@login_required
def api_account():
    user_info = UserInfo.query.filter_by(user_id=current_user.id).first()
    return jsonify({
        'user_info': {
            'name': user_info.name if user_info else None,
            'address': user_info.address if user_info else None
        }
    })

@main.route('/api/account/password', methods=['POST'])
@login_required
def api_account_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    if bcrypt.checkpw(current_password.encode('utf-8'), current_user.password.encode('utf-8')):
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        current_user.password = hashed.decode('utf-8')
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Incorrect current password'})

@main.route('/api/account/info', methods=['POST'])
@login_required
def api_account_info():
    name = bleach.clean(request.form['name'])
    address = bleach.clean(request.form['address'])
    user_info = UserInfo.query.filter_by(user_id=current_user.id).first()
    if not user_info:
        user_info = UserInfo(user_id=current_user.id, name=name, address=address)
        db.session.add(user_info)
    else:
        user_info.name = name
        user_info.address = address
    db.session.commit()
    return jsonify({'success': True})
