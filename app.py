"""
Stephanie Liu
Requirements:
DONE 1) Test user: lhhung@uw.edu qwerty
DONE 2) User logs in to a dashboard / landing page
DONE 3) Dashboard contains form to enter date and maximum number of results.
    Date verified with flask_wtf, max entries between 1-20.
DONE 4) Validated data queries wiki api to get birthdays shared by famous people.
    Sorted by closeness to entry year of birth.
    Thumbnail, name, birth year returned in table.
DONE 5) Navigation bar, disables landing page unless accessed by login.
DONE 6) App must run in docker container.
DONE 7) Submit working URL for app deployed to cloud.
DONE Å8) Github repo with all necessary files.
DONE 9) When URL browsed, should redirect to login, then to registration page.
"""

from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange
from flask_login import login_user, login_required, logout_user
from models import db, login, UserModel
import wiki


class EmailPassForm(FlaskForm):
    email = StringField(label="Enter email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Enter password", validators=[DataRequired(), Length(min=6, max=16)])


class LoginForm(EmailPassForm):
    submit = SubmitField(label="Login")


class RegisterForm(EmailPassForm):
    submit = SubmitField(label="Register")


class BirthDateNums(FlaskForm):
    birthday = DateField(label="Enter birthday", validators=[DataRequired()])
    num_results = IntegerField(label="Number of results", validators=[DataRequired(), NumberRange(min=1, max=20)])
    submit = SubmitField(label="Search")


app = Flask(__name__)
app.secret_key = "a secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login.init_app(app)


@app.route("/home", methods=['GET', 'POST'])
@login_required
def find_births():
    form = BirthDateNums()
    if form.validate_on_submit():
        if request.method == "POST":
            # <td class="align-middle">{{ loop.index0 +1 }}</td> was in home in <tr>
            birthday = request.form["birthday"]
            num_results = request.form["num_results"]
            month = birthday[5:7] + "/" + birthday[8:10]
            year = birthday[0:4]
            return render_template("home.html", form=form, myData=wiki.find_births(month, year, num_results))
    return render_template("home.html", myData=wiki.find_births("02/29", "1986", 0), form=form)


@app.route("/")
def redirect_to_login():
    return redirect("/login")


def add_user(email, password):
    # check if email or username exits
    user = UserModel()
    user.set_password(password)
    user.email = email
    db.session.add(user)
    db.session.commit()


@app.before_first_request
def create_table():
    """
    Creates database if it doesn't already exist including a default user.
    """
    db.create_all()
    user = UserModel.query.filter_by(email="lhhung@uw.edu").first()
    if user is None:
        add_user("lhhung@uw.edu", "qwerty")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            user = UserModel.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                login_user(user)
                return redirect('/home')
    return render_template("login.html", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            user = UserModel.query.filter_by(email=email).first()
            if user is None:
                add_user(email, password)
                flash("Thank you for registering!")
                return redirect('/login')
            elif user is not None and user.check_password(password):
                flash("Welcome back!")
                login_user(user)
                return redirect('/home')
            else:
                flash("User already exists and you used an incorrect password.")
    return render_template("register.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
