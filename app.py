import os
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'gwgatausecretkeybuatapa'

db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    desc = db.Column(db.String)
    time = db.Column(db.DateTime)
    capacity = db.Column(db.Integer)
    registered = db.Column(db.Integer, default=0)

class Participations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user = db.relationship('Users')
    event = db.relationship('Events')

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
    if not Events.query.all():
        #kalau belom ada event apa2, tambahin bbrp event custom
        ev = [Events(name='TechFest 2024' , desc='A technology conference bringing together industry leaders, innovators, and enthusiasts to explore the latest advancements in technology. Expect keynote speeches, workshops, and networking opportunities.' , time=datetime(2024, 2, 27, 13, 0, 0) , capacity=85), 
              Events(name='Art Unleashed' , desc='An art exhibition showcasing the works of emerging artists from around the world. Visitors can enjoy a variety of art styles and mediums, and even purchase pieces to support the artists.' , time=datetime(2024, 3, 3, 16, 0, 0) , capacity=105), 
              Events(name='Global Food Fair' , desc='A culinary event celebrating diverse cuisines from around the globe. Food stalls will offer dishes from different countries, cooking demonstrations, and cultural performances.' , time=datetime(2024, 3, 8, 11, 0, 0) , capacity=160), 
              Events(name='Green Marathon' , desc='A charity run promoting environmental awareness and sustainability. Participants can join various categories, and proceeds will go towards supporting environmental conservation projects.' , time=datetime(2024, 2, 29, 8, 0, 0) , capacity=75), 
              Events(name='Jazz Under the Stars' , desc='An outdoor jazz concert featuring renowned jazz musicians and bands. Enjoy a night of great music under the starlit sky, with food and drinks available for purchase.' , time=datetime(2024, 3, 11, 19, 0, 0) , capacity=195)]
        #fun fact, nama + deskripsi event2 ini aku bikin pake copilot (ga sempet ngarang sendiri cuy)
        for e in ev:
            db.session.add(e)
        db.session.commit()
        #soalnya, yg disuruh cuma biar user bisa lihat/daftar/hapus event
        #jadi aku ga bikin sistem buat adminnya nambahin event2
        #makanya sebagai gantinya biar Event ga kosong pakenya ini
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

@app.route("/events", methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        pass; #route ini sekarang baru buat display semua event, belom ada yang pake POST
    return render_template("/events.html", user=current_user, eventlist=Events.query.all())
    
if __name__ == '__main__':
    app.run(debug=True)