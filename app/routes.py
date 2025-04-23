from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user, login_user, logout_user
import bleach
import bcrypt
from datetime import datetime, date
from app.models import User, Resource, Goal, Project, Progress, db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    resources = Resource.query.filter_by(user_id=current_user.id).all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    projects = Project.query.filter_by(user_id=current_user.id).all()
    progress = Progress.query.filter_by(user_id=current_user.id).first()
    completed_goals = len([g for g in goals if g.progress == 100])
    total_goals = len(goals)
    categories = ['Docker', 'CI/CD', 'Security', 'Kubernetes', 'Cloud']
    goal_counts = {cat: len([g for g in goals if g.category == cat and g.progress == 100]) for cat in categories}
    return render_template('dashboard.html', resources=resources, goals=goals, projects=projects,
                         progress=progress, completed_goals=completed_goals, total_goals=total_goals,
                         goal_counts=goal_counts, categories=categories)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if not Progress.query.filter_by(user_id=user.id).first():
                progress = Progress(user_id=user.id, total_points=0, milestone='Beginner')
                db.session.add(progress)
                db.session.commit()
            return redirect(url_for('main.index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@main.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(username=username, password=hashed.decode('utf-8'))
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('main.login'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/resources/add', methods=['POST'])
@login_required
def add_resource():
    data = request.form
    clean_title = bleach.clean(data['title'])
    clean_notes = bleach.clean(data['notes'])
    clean_tags = bleach.clean(data['tags'])
    resource = Resource(
        title=clean_title,
        url=data['url'],
        notes=clean_notes,
        category=data['category'],
        tags=clean_tags,
        user_id=current_user.id
    )
    db.session.add(resource)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/goals/add', methods=['POST'])
@login_required
def add_goal():
    data = request.form
    clean_title = bleach.clean(data['title'])
    goal = Goal(
        title=clean_title,
        deadline=datetime.strptime(data['deadline'], '%Y-%m-%d').date() if data['deadline'] else None,
        points=int(data['points']),
        category=data['category'],
        user_id=current_user.id
    )
    db.session.add(goal)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/goals/update/<int:id>', methods=['POST'])
@login_required
def update_goal(id):
    goal = Goal.query.get_or_404(id)
    if goal.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.form
    goal.progress = int(data['progress'])
    goal.status = data['status']
    if goal.progress == 100 and goal.status == 'Completed':
        progress = Progress.query.filter_by(user_id=current_user.id).first()
        progress.total_points += goal.points
        update_milestone(progress)
        db.session.commit()
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/projects/add', methods=['POST'])
@login_required
def add_project():
    data = request.form
    clean_title = bleach.clean(data['title'])
    clean_description = bleach.clean(data['description'])
    clean_notes = bleach.clean(data['notes'])
    project = Project(
        title=clean_title,
        description=clean_description,
        repo_url=data['repo_url'],
        notes=clean_notes,
        points=int(data['points']),
        completed=data.get('completed') == 'on',
        user_id=current_user.id
    )
    if project.completed:
        progress = Progress.query.filter_by(user_id=current_user.id).first()
        progress.total_points += project.points
        update_milestone(progress)
    db.session.add(project)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/checkin', methods=['POST'])
@login_required
def checkin():
    progress = Progress.query.filter_by(user_id=current_user.id).first()
    today = date.today()
    if not progress.last_checkin or progress.last_checkin != today:
        progress.total_points += 5
        progress.last_checkin = today
        update_milestone(progress)
        db.session.commit()
    return redirect(url_for('main.index'))

def update_milestone(progress):
    if progress.total_points >= 1000:
        progress.milestone = 'DevSecOps Expert'
    elif progress.total_points >= 500:
        progress.milestone = 'CI/CD Pro'
    elif progress.total_points >= 200:
        progress.milestone = 'Docker Pro'
    elif progress.total_points >= 100:
        progress.milestone = 'Docker Novice'

@main.route('/export', methods=['GET'])
@login_required
def export():
    resources = Resource.query.filter_by(user_id=current_user.id).all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    projects = Project.query.filter_by(user_id=current_user.id).all()
    progress = Progress.query.filter_by(user_id=current_user.id).first()
    data = {
        'resources': [{'id': r.id, 'title': r.title, 'url': r.url, 'notes': r.notes, 'category': r.category, 'tags': r.tags} for r in resources],
        'goals': [{'id': g.id, 'title': g.title, 'deadline': str(g.deadline), 'progress': g.progress, 'points': g.points, 'status': g.status, 'category': g.category} for g in goals],
        'projects': [{'id': p.id, 'title': p.title, 'description': p.description, 'repo_url': p.repo_url, 'notes': p.notes, 'points': p.points, 'completed': p.completed} for p in projects],
        'progress': {'total_points': progress.total_points, 'milestone': progress.milestone}
    }
    return jsonify(data)

@main.route('/import', methods=['POST'])
@login_required
def import_data():
    data = request.json
    for res in data['resources']:
        resource = Resource(
            title=bleach.clean(res['title']),
            url=res['url'],
            notes=bleach.clean(res['notes']),
            category=res['category'],
            tags=bleach.clean(res['tags']),
            user_id=current_user.id
        )
        db.session.add(resource)
    for g in data['goals']:
        goal = Goal(
            title=bleach.clean(g['title']),
            deadline=datetime.strptime(g['deadline'], '%Y-%m-%d').date() if g['deadline'] else None,
            progress=g['progress'],
            points=g['points'],
            status=g['status'],
            category=g['category'],
            user_id=current_user.id
        )
        db.session.add(goal)
    for p in data['projects']:
        project = Project(
            title=bleach.clean(p['title']),
            description=bleach.clean(p['description']),
            repo_url=p['repo_url'],
            notes=bleach.clean(p['notes']),
            points=p['points'],
            completed=p['completed'],
            user_id=current_user.id
        )
        db.session.add(project)
    progress = Progress.query.filter_by(user_id=current_user.id).first()
    progress.total_points = data['progress']['total_points']
    progress.milestone = data['progress']['milestone']
    db.session.commit()
    return redirect(url_for('main.index'))
