"""
Stephanie Liu
Requirements:
The login fields:
DONE - Username and password.
DONE - Submit button and a link to optionally register which redirects to the registration page.
DONE - Login redirects to dashboard.  Dashboard inaccessible without login.
DONE - Login failed message.

DONE - Username should be at least 6 characters and no more than 20 characters.
DONE - Passwords should be at least 8 characters. (I maxed at 16)

The registration page should have:
DONE username
DONE email
DONE password
DONE register button.
DONE user should be redirected to the login page (also added redirects to home if registered with sign in info)

DONE - User logout.

DONE - Username, password and email should be put into a database, password should be encrypted.

Deployed in production mode with gunicorn in the same container as flask, and nginx in a separate container.
A docker-compose file should be used to orchestrate the deployment.

You should submit a working url for your assignment app which is deployed to the cloud.
When I browse your url with no endpoint, it should redirect me to the login page and then to the registration page.

You should have a github repo with all the necessary files (including  Dockerfiles for all the containers).

You don’t need to push the containers to DockerHub though you can if you want and it makes it easier for me to figure
out where you went wrong if you have problems.
"""

from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange
from flask_login import login_user, login_required, logout_user
from models import db, login, UserModel
import wiki


class EmailPassForm(FlaskForm):
    username = StringField(label="Enter username", validators=[DataRequired(), Length(min=6, max=20)])
    password = PasswordField(label="Enter password", validators=[DataRequired(), Length(min=8, max=16)])


class LoginForm(EmailPassForm):
    submit = SubmitField(label="Login")


class RegisterForm(EmailPassForm):
    email = StringField(label="Enter email", validators=[DataRequired(), Email()])
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


def add_user(username, email, password):
    # check if email or username exits
    user = UserModel()
    user.set_password(password)
    user.username = username
    user.email = email
    db.session.add(user)
    db.session.commit()


@app.before_first_request
def create_table():
    """
    Creates database if it doesn't already exist including a default user.
    """
    db.create_all()
    # user = UserModel.query.filter_by(email="lhhung@uw.edu").first()
    # if user is None:
    #     add_user("lhhung@uw.edu", "qwerty")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = UserModel.query.filter_by(username=username).first()
            if user is not None and user.check_password(password):
                login_user(user)
                return redirect('/home')
            else:
                flash("Login attempt failed. Please check username and password, then try again.")
    return render_template("login.html", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if request.method == "POST":
            email = request.form["email"]
            username = request.form["username"]
            password = request.form["password"]
            user_email = UserModel.query.filter_by(email=email).first()
            user_name = UserModel.query.filter_by(username=username).first()
            if user_email is None and user_name is None:
                add_user(username=username, email=email, password=password)
                flash("Thank you for registering!")
                return redirect('/login')
            elif user_name is not None and user_name.check_password(password):
                flash("Welcome back!  Your account is already registered.")
                login_user(user_name)
                return redirect('/home')
            elif user_name is not None and user_email is None:
                flash("Username is already taken.  Please choose another one.")
            elif user_email is not None:
                flash("Email is already registered, please check your user name or password and try signing in.")
                return redirect('/login')
            else:
                flash("Please try another username or email address, as these are already registered.")
    return render_template("register.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
