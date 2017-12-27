# encoding = utf-8

from flask import Flask,render_template,url_for,request,redirect,session
from werkzeug.utils import secure_filename
import config
from models import User, Source
from exts import db
from decorators import login_require
from sqlalchemy import desc
import os, datetime, platform


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
@app.route('/index/')
@login_require
def index():
    user_id = session.get('user_id')
    sourcefilelist = Source.query.filter(Source.owner_id == user_id).order_by(desc(Source.id)).all()
    return render_template('index.html', sources = sourcefilelist)


@app.route('/data/')
@login_require
def data():
    return render_template('data.html')


@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username == username, User.password == password).first()
        if user:
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return 'username or password is wrong'


@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter(User.email == email).first()
        if user:
            return 'email is already registered'
        else:
            if password1 != password2:
                return 'Please confirm password!'
            else:
                user = User(email=email, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/upload/', methods = ['POST'])
def upload():
    uf = request.files['input-b1']
    filename = secure_filename(uf.filename)
    currentpath = os.path.dirname(__file__)
    savepath = currentpath + '\\uploadfolder\\' + filename
    uf.save(savepath)
    # update db
    source = Source(path=savepath,filename=filename)
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    source.owner = user
    db.session.add(source)
    db.session.commit()
    return redirect(url_for('data'))


@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user':user}
    return {}


if __name__ == '__main__':
    app.run()
