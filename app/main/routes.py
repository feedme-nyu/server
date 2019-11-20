import os
from flask import render_template, request
from app.main.forms import *
from app.main import bp

'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''

@bp.route('/')
def home():
    return render_template('pages/placeholder.home.html')


@bp.route('/about')
def about():
    return render_template('pages/placeholder.about.html')

@bp.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)

@bp.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)

@bp.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

@bp.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500

@bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
