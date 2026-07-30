from werkzeug.security import generate_password_hash
from flask import Flask, render_template
from models import db,User
from flask import Flask, render_template, redirect, url_for, flash
from forms import RegistrationForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense_tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register",methods =["GET","POST"])
def register():
    form =RegistrationForm()

    if form.validate_on_submit():
        print("Form validation passed!")

        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            print("User already exists!")
            flash("Email already registered.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(form.password.data)
        print("Password hashed!")

        new_user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        print("User saved successfully!")

        flash("Account created successfully!", "success")
        return redirect(url_for("home"))

    return render_template("register.html",form=form)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)