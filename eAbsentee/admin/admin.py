import os
from flask import Blueprint, render_template, request, make_response, flash, redirect, session, url_for
from flask_login import login_required, logout_user, current_user, login_user
from ..app import db, bcrypt, login_manager
from ..form.models import User
from .models import AdminUser
from .utils import get_users, get_groups
from dotenv import load_dotenv
load_dotenv()

admin_bp = Blueprint(
    'admin_bp', __name__, template_folder='templates', static_folder='static'
)

# @admin_bp.route('/interface/', methods=['GET', 'POST'])
# @login_required
# def admin_interface():
#     return render_template('interface.html', users=User.query.all())

# @admin_bp.route('/test/', methods=['GET', 'POST'])
# @login_required
# def test():
#     create_map()
#     return render_template('test.html')

@admin_bp.route('/maps/', methods=['GET', 'POST'])
@login_required
def maps():
    groups = get_groups()
    mapbox_key = os.environ["MAPBOX_KEY"]
    if request.method == 'POST':
        users = get_users(group=request.form["group"], date=request.form["date"])
        return render_template('map.html', groups=groups, users=users, mapbox_key=mapbox_key)
    if request.method == 'GET':
        return render_template('map.html', groups=groups, mapbox_key=mapbox_key)

@admin_bp.route('/login/', methods=['GET', 'POST'])
@login_manager.unauthorized_handler
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.maps'))

    if request.method == 'POST':
        user = AdminUser.query.filter_by(email=request.form['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user, remember=True)
            return redirect(url_for('admin_bp.maps'))
        else:
            flash('Invalid username/password combination')
            return redirect(url_for('admin_bp.login'))
    elif request.method == 'GET':
        return render_template('login.html')

@admin_bp.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.admin_interface'))

    if request.method == 'POST':
        existing_user = AdminUser.query.filter_by(id=request.form['email']).first()
        if existing_user is None:
            new_admin = AdminUser(
                email=request.form['email'],
                password=bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            )
            db.session.add(new_admin)
            db.session.commit()
            login_user(new_admin, remember=True)
            return redirect('/interface/')
        else:
            flash('A user already exists with that email address.', 'danger')
            return render_template('register.html')
    elif request.method == 'GET':
        return render_template('register.html')
