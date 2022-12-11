from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import login_user
from flask_login import UserMixin
from flask_login import LoginManager
from flask_login import login_required
from flask_login import logout_user
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash



app = Flask(__name__)
app.secret_key = 'some secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)


class BigShop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    price = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(30), nullable=False)
    image = db.Column(db.String(300), nullable=False)
    tell = db.Column(db.String(15))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<BigShop %r>' % self.id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    bigShop = BigShop.query.order_by(BigShop.date.desc()).all()
    return render_template('index.html', bigShop=bigShop)


@app.route("/product/<int:id>")
def product(id):
    bigShop = BigShop.query.get(id)
    return render_template('product.html', bigShop=bigShop)


@app.route("/login", methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')

            return redirect(next_page)
        else:
            flash('Login or password is not correct')
    else:
        flash('Please fill login and password fields')
    return render_template('login.html')


@app.route("/register", methods=['POST', 'GET'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == "POST":
        if not (login or password or password2):
            flash('Please fill all fields!')
        elif password != password2:
            flash('Password are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return render_template('index.html')


@app.route("/add_product",  methods=['POST', 'GET'])
@login_required
def add_product():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']
        image = request.form['image']
        tell = request.form['tell']

        bigShop = BigShop(title=title, price=price, description=description, image=image, tell=tell)

        try:
            db.session.add(bigShop)
            db.session.commit()
            return redirect('/')
        except:
            return "При добавление товара произошла ошибка"
    else:
        return render_template('add_product.html')


@app.route("/about")
def about():
    return render_template('about.html')

@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return response


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)
