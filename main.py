from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
import random
import json
import plotly
from datetime import datetime
from Coffee import vytvor_graf
from Coffee_2D import vytvor_graf_2D
from Coffee_United import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coffee.db'
app.config['SECRET_KEY'] = 'sdsd684f3s687ed445FDFASDF'
db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Coffee(db.Model):
    __tablename__ = "coffee"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    name = db.Column(db.Integer, db.ForeignKey("users.username"))
    combination = db.Column(db.String(60), unique=True, nullable=False)
    amount_coffee = db.Column(db.Integer)  # 1-5 zrn kávy
    amount_water = db.Column(db.Integer)  # 25-100ml po 25 krok
    amount_clean_water = db.Column(db.Integer)  # 0-100ml po 25 krok
    acidity = db.Column(db.Integer)
    bitterness = db.Column(db.Integer)
    strong = db.Column(db.Integer)
    taste = db.Column(db.Integer)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Comment(UserMixin, db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    user_comment = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.String(500), nullable=False)
    time = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


def random_coffee():
    name = current_user.username
    db_data = local_data()
    random_choice = random_coffee_model(db_data, name)
    coffee = random_choice[0]
    water = random_choice[1]
    clean_water = random_choice[2]
    if coffee == 1:
        random_coffee = f"Dnes doporučuji {coffee} zrnko kávy s {water} ml vody a {clean_water} ml čisté vody"
    elif coffee == 5:
        random_coffee = f"Dnes doporučuji {coffee} zrnek kávy s {water} ml vody a {clean_water} ml čisté vody"
    else:
        random_coffee = f"Dnes doporučuji {coffee} zrnka kávy s {water} ml vody a {clean_water} ml čisté vody"
    return random_coffee


def random_coffee_model(data, user):
    victor = []
    for i in [1, 2, 3, 4, 5]:
        for j in [25, 50, 75, 100]:
            for k in [0, 25, 50, 75, 100]:
                victor.append([i, j, k])
    victor_all = victor.copy()
    victor_mine = victor.copy()
    for dictionary in data:
        if [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']] in [
            victor_all[i][0:3] for i, element in enumerate(victor_all)]:
            victor_all.remove(
                [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])
        if dictionary['user'] == user and [dictionary['amount_coffee'], dictionary['amount_water'],
                                           dictionary['amount_clean_water']] in [victor_mine[i][0:3] for i, element in
                                                                                 enumerate(victor_mine)]:
            victor_mine.remove(
                [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])

    if len(victor_all):
        return random.choice(victor_all)
    elif len(victor_mine):
        return random.choice(victor_mine)
    else:
        return random.choice(victor)


@app.route('/')
def home():
    if current_user.is_active == False:
        return render_template("authentication.html",
                               current_user=current_user)
    all_coffee = db.session.query(Coffee).filter(
        Coffee.name.like(current_user.username))
    users = db.session.query(User).all()
    coffee = random_coffee()
    return render_template("index.html", coffees=all_coffee, current_user=current_user, users=users,
                           random_coffee=coffee)


@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method == "POST":
        searching_word = request.form["username"]
        if searching_word == "all":
            filter_coffees = db.session.query(Coffee).all()
        else:
            filter_coffees = db.session.query(Coffee).filter(
                Coffee.name.like(f"%{searching_word}%"))
        users = db.session.query(User).all()
        return render_template("index.html", coffees=filter_coffees,
                               current_user=current_user, users=users)


@app.route('/show-amount', methods=["GET", "POST"])
def show_amount():
    if request.method == "POST":
        amount_coffee = request.form["amount_coffee"]
        if amount_coffee == "all":
            filter_coffees = db.session.query(Coffee).all()
        else:
            filter_coffees = db.session.query(Coffee).filter(
                Coffee.amount_coffee.like(f"%{amount_coffee}%"))
    return render_template("index.html", coffees=filter_coffees)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            new_user = User(
                username=request.form["username"],
                password=request.form["password"]
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
        except:
            return render_template("register.html", current_user=current_user)
    return render_template("register.html", current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/add', methods=["GET", "POST"])
def add():
    amount_coffee = request.form.get("amount_coffee")
    amount_water = request.form.get("amount_water")
    amount_clean_water = request.form.get("amount_clean_water")
    acidity = request.form.get("acidity")
    bitterness = request.form.get("bitterness")
    strong = request.form.get("strong")
    taste = request.form.get("taste")
    name = current_user.username
    combination = f"{name}-{amount_coffee}-{amount_water}-{amount_clean_water}"

    new_review = Coffee(
        amount_coffee=amount_coffee,
        amount_water=amount_water,
        amount_clean_water=amount_clean_water,
        acidity=acidity,
        bitterness=bitterness,
        strong=strong,
        taste=taste,
        combination=combination,
        user_id=current_user.id,
        name=name
    )
    try:
        db.session.add(new_review)
        db.session.commit()
    except:
        flash("Tuto kávu jsi již ohodnotil")

    return redirect(url_for("home"))


@app.route('/show_all', methods=["GET", "POST"])
def show_all():
    all_coffee = db.session.query(Coffee).all()
    users = db.session.query(User).all()
    coffee = random_coffee()
    return render_template("index.html", coffees=all_coffee, current_user=current_user, users=users,
                           random_coffee=coffee)


@app.route('/show_my', methods=["GET", "POST"])
def show_my():
    return redirect(url_for("home"))


@app.route('/data')
def data():
    reviews = Coffee.query.all()
    output = json.dumps(format_dat(reviews))
    return output


def local_data():
    reviews = Coffee.query.all()
    output = format_dat(reviews)
    return output


def format_dat(reviews):
    output = [{"user": coffee.name, "amount_coffee": coffee.amount_coffee, "amount_water": coffee.amount_water,
               "amount_clean_water": coffee.amount_clean_water, "acidity": coffee.acidity,
               "bitterness": coffee.bitterness,
               "strong": coffee.strong, "taste": coffee.taste} for
              coffee in reviews]
    return output


@app.route('/graph', methods=["GET", "POST"])
def graph():
    db_data = local_data()
    users = db.session.query(User).all()
    if request.method == "POST":
        user = request.form["username"]
        param = request.form["parametr"]
    ## parametry pro vytvoření grafu
    else:
        user = 'all'
        param = 'taste'
    ## vytvoreni grafu na web
    fig = vytvor_graf(db_data, user, param)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('graph.html', graphJSON=graphJSON, user=user, param=param, users=users)


@app.route('/graph2d', methods=["GET", "POST"])
def graph2d():
    ## parametry pro vytvoření grafu
    db_data = local_data()
    user = 'all'
    param = 'taste'
    ## vytvoreni grafu na web
    if request.method == "POST":
        amount_coffee = int(request.form.get("amount_coffee"))
        amount_water = int(request.form.get("amount_water"))
        amount_clean_water = int(request.form.get("amount_clean_water"))
    else:
        amount_coffee = 3
        amount_water = 50
        amount_clean_water = 50
    info = [amount_coffee, amount_water, amount_clean_water]
    fig = vytvor_graf_2D(db_data, user, param, 3, 50, 50)
    graphJSON1 = json.dumps(fig[0], cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig[1], cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON3 = json.dumps(fig[2], cls=plotly.utils.PlotlyJSONEncoder)
    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('graph2d.html', graphJSON=[graphJSON1, graphJSON2, graphJSON3], user=user, param=param,
                           info=info)
    # info=[coffee]
    # return render_template('graph2d.html', graphJSON=graphJSON, user=user, param=param,info=info)


@app.route('/stats')
def stats():
    data = make_stats()
    taste = data["taste_max"]
    acidity = data["acidity_max"]
    bitterness = data["bitterness_max"]
    strong = data["strong_max"]
    taste_min = data["taste_min"]
    acidity_min = data["acidity_min"]
    bitterness_min = data["bitterness_min"]
    strong_min = data["strong_min"]
    popisky = ["Nejchutnější", "Nejvíce kyselá", "Nejvíce hořká", "Nejsilnější", "Nejméně chutná", "Nejméně kyselá",
               "Nejméně hořká", "Nejméně silná"]
    statistiky = [taste, acidity, bitterness, strong, taste_min, acidity_min, bitterness_min, strong_min]
    return render_template("statistics.html", statistiky=statistiky, popisky=popisky, delka_seznamu=len(popisky))


def make_stats():
    data = local_data()
    output = {}
    for property in ['acidity', 'bitterness', 'strong', 'taste']:
        vector = []
        for dictionary in data:
            if [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']] in [
                vector[i][0:3] for i, element in enumerate(vector)]:
                i = [vector[i][0:3] for i, element in enumerate(vector)].index(
                    [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water']])
                vector[i].append(dictionary[property])
            else:
                vector.append(
                    [dictionary['amount_coffee'], dictionary['amount_water'], dictionary['amount_clean_water'],
                     dictionary[property]])
        victor = []
        for i, element in enumerate(vector):
            if len(element[3:]) > 1:
                sub_vector = element[0:3]
                sub_vector.append(round(sum(element[3:]) / len(element[3:]), 1))  # element[0:3]
                victor.append(sub_vector)
        output[property + '_min'] = [i for i in victor if i[-1] == min(victor, key=lambda x: x[-1])[-1]]
        output[property + '_max'] = [i for i in victor if i[-1] == max(victor, key=lambda x: x[-1])[-1]]

    print(output)
    return output


@app.route('/delete')
def delete():
    coffee_id = request.args.get("id")
    coffee_to_delete = Coffee.query.get(coffee_id)
    db.session.delete(coffee_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/delete-comment')
def delete_comment():
    comment_id = request.args.get("id")
    comment_to_delete = Comment.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for("forum"))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    coffee_id = request.args.get("id")
    coffee_selected = Coffee.query.get(coffee_id)
    stats = [coffee_selected.name, coffee_selected.amount_coffee, coffee_selected.amount_water,
             coffee_selected.amount_clean_water]
    print(stats)
    if request.method == "POST":
        coffee_to_update = coffee_selected
        coffee_to_update.acidity = request.form["acidity"]
        coffee_to_update.bitterness = request.form["bitterness"]
        coffee_to_update.strong = request.form["strong"]
        coffee_to_update.taste = request.form["taste"]
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", coffee=coffee_selected,
                           current_user=current_user, stats=stats)


@app.route('/forum', methods=["GET", "POST"])
def forum():
    if request.method == "POST":
        new_comment = Comment(
            user_comment=current_user.username,
            comment=request.form["komentar"],
            time=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('forum'))
    comments = db.session.query(Comment).all()
    return render_template("forum.html", comments=comments)


if __name__ == '__main__':
    app.run(debug=True)
