import os
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'gwgatausecretkeybuatapa'

db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

class Events(db.Model):
    name = db.Column(db.String, primary_key=True)
    desc = db.Column(db.String)
    time = db.Column(db.DateTime)
    capacity = db.Column(db.Integer)
    registered = db.Column(db.Integer)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.route("/")
def home():
    return render_template("/home.html", user=current_user)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        uname = Users.query.filter_by(username=username).first()

        if uname:
            flash('Username already registered!')
        elif len(username) < 1:
            flash('Must enter username!')
        elif len(password) < 1:
            flash('Must enter password!')
        elif len(confirmation) < 1:
            flash('Must confirm password.')
        elif password != confirmation:
            flash('Password confirmation must match.')
        else:
            registree = Users(username=username, password=generate_password_hash(password))
            db.session.add(registree)
            db.session.commit()
            login_user(registree, remember="True")
            flash('Succesfully registered!')
            return redirect(url_for('home'))

    return render_template("/register.html", user=current_user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        uname = Users.query.filter_by(username=username).first()

        if uname:
            if check_password_hash(uname.password, password):
                login_user(uname, remember="True")
                flash('Succesfully logged in!')
                return redirect(url_for('home'))
            else:
                flash('Incorrect password')
        else:
            flash('User not found')

    return render_template("/login.html", user=current_user)

@app.route("/logout")
def logout():
    logout_user()
    flash('Succesfully logged out!')
    return redirect(url_for('login'))
    
if __name__ == '__main__':
    app.run(debug=True)