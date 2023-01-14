from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from forms import *
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config['SECRET_KEY'] = '1234567890'
ckeditor = CKEditor(app)
Bootstrap5(app)
login_manager = LoginManager(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    kanbans = db.relationship('KanbanTables', back_populates='owner')


class KanbanTables(db.Model):
    __tablename__ = "tables"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner = db.relationship("User", back_populates="kanbans")

    kanban_name = db.Column(db.String(100), nullable=False)
    kanban_info = db.Column(db.String(1000))
    kanban_progress = db.Column(db.Integer)

    title_cards = db.relationship("TitleCard", back_populates="parent_kanban")
    title_text_cards = db.relationship("TitleTextCard", back_populates="parent_kanban")
    title_list_cards = db.relationship("TitleListCard", back_populates="parent_kanban")
    title_img_cards = db.relationship("TitleImgCard", back_populates="parent_kanban")


class TitleCard(db.Model):
    __tablename__ = "title_cards"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    position = db.Column(db.Integer)
    progress = db.Column(db.Integer)

    table_id = db.Column(db.Integer, db.ForeignKey("tables.id"))
    parent_kanban = db.relationship("KanbanTables", back_populates="title_cards")


class TitleTextCard(db.Model):
    __tablename__ = "title_text_cards"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.String(600))
    position = db.Column(db.Integer)
    progress = db.Column(db.Integer)

    table_id = db.Column(db.Integer, db.ForeignKey("tables.id"))
    parent_kanban = db.relationship("KanbanTables", back_populates="title_text_cards")


class TitleListCard(db.Model):
    __tablename__ = "title_list_cards"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    lists = db.Column(db.String(1000))
    position = db.Column(db.Integer)
    progress = db.Column(db.Integer)

    table_id = db.Column(db.Integer, db.ForeignKey("tables.id"))
    parent_kanban = db.relationship("KanbanTables", back_populates="title_list_cards")


class TitleImgCard(db.Model):
    __tablename__ = "title_img_cards"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    img = db.Column(db.String(300))
    position = db.Column(db.Integer)
    progress = db.Column(db.Integer)

    table_id = db.Column(db.Integer, db.ForeignKey("tables.id"))
    parent_kanban = db.relationship("KanbanTables", back_populates="title_img_cards")


with app.app_context():
    db.create_all()
    db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/', methods=["GET", "POST"])
def home():
    form = RegisterForm()

    if form.validate_on_submit():
        # Check if exists
        if User.query.filter_by(email=form.email.data).first():

            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('home')+"#sign-up")

        # Add new user
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8)

        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('index.html', form=form)


@app.context_processor
def inject_user():
    kanban_form = NewKanbanForm()
    if kanban_form.validate_on_submit():
        new_kanban = KanbanTables(
            user_id=current_user.id,
            kanban_name=kanban_form.kanban_name.data,
            kanban_info=kanban_form.kanban_info.data,
            kanban_progress=0,
        )
        db.session.add(new_kanban)
        db.session.commit()

    return dict(kanban_form=kanban_form)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if exists
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('register'))

        # Add new user
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8)

        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_email = form.email.data
        login_password = form.password.data
        user = User.query.filter_by(email=login_email).first()

        if user:
            if check_password_hash(user.password, login_password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Wrong Password, please try again.')
                return redirect(url_for('login'))
        else:
            flash('That Email does not exist, please try again.')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@login_required
@app.route('/profile', methods=["GET", "POST"])
def profile():
    user = User.query.get(current_user.id)
    return render_template('profile.html', user=user)


@login_required
@app.route('/kanban/<int:kanban_id>', methods=["GET", "POST"])
def kanban(kanban_id):
    requested_kanban = KanbanTables.query.get(kanban_id)
    title_card_form = NewTitleCard()
    text_card_form = NewTextCard()
    img_card_form = NewImgCard()

    if not current_user.is_authenticated:
        flash("You need to login or register to access that page.")
        return redirect(url_for("login"))

    if title_card_form.validate_on_submit():
        new_title_card = TitleCard(
            table_id=kanban_id,
            title=title_card_form.card_title.data,
            position=0,
            progress=0,
        )
        db.session.add(new_title_card)
        db.session.commit()

    if text_card_form.validate_on_submit():
        new_text_card = TitleTextCard(
            table_id=kanban_id,
            title=text_card_form.text_card_title.data,
            text=text_card_form.card_text.data,
            position=0,
            progress=0,
        )
        db.session.add(new_text_card)
        db.session.commit()

    if img_card_form.validate_on_submit():
        new_img_card = TitleImgCard(
            table_id=kanban_id,
            title=img_card_form.img_card_title.data,
            img=img_card_form.card_img_url.data,
            position=0,
            progress=0,
        )
        db.session.add(new_img_card)
        db.session.commit()

    return render_template('task-page.html',
                           title_card_form=title_card_form,
                           text_card_form=text_card_form,
                           img_card_form=img_card_form,
                           requested_kanban=requested_kanban, )


@login_required
@app.route("/edit/<int:kanban_id>/<table>/<int:card_id>/<int:progress>", methods=["GET", "POST"])
def edit_card(kanban_id, table, card_id, progress):
    card = ''
    edit_form = ''

    if table == 'title_cards':
        card = TitleCard.query.get(card_id)
        edit_form = EditCard(card_title_edited=card.title, progress=progress, position=card.position)
    elif table == 'title_text_cards':
        card = TitleTextCard.query.get(card_id)
        edit_form = EditCard(card_title_edited=card.title, card_text_edited=card.text, progress=progress,
                             position=card.position)
    elif table == 'title_img_cards':
        card = TitleImgCard.query.get(card_id)
        edit_form = EditCard(card_title_edited=card.title, card_img_url_edited=card.img, progress=progress,
                             position=card.position)

    if edit_form.validate_on_submit():
        if table == 'title_cards':
            card.title = edit_form.card_title_edited.data
        elif table == 'title_text_cards':
            card.title = edit_form.card_title_edited.data
            card.text = edit_form.card_text_edited.data
        elif table == 'title_img_cards':
            card.title = edit_form.card_title_edited.data
            card.img = edit_form.card_img_url_edited.data
        card.progress = int(edit_form.progress.data)
        card.position = int(edit_form.position.data)

        db.session.commit()

        return redirect(url_for("kanban", kanban_id=kanban_id))

    return render_template("edit-card.html", edit_form=edit_form, table_type=table)


@login_required
@app.route("/delete/<int:kanban_id>/<table>/<int:card_id>")
def delete_card(kanban_id, table, card_id):
    card = ''

    if table == 'title_cards':
        card = TitleCard.query.get(card_id)
    elif table == 'title_text_cards':
        card = TitleTextCard.query.get(card_id)
    elif table == 'title_img_cards':
        card = TitleImgCard.query.get(card_id)

    db.session.delete(card)
    db.session.commit()

    return redirect(url_for('kanban', kanban_id=kanban_id))


@login_required
@app.route("/progress/<int:kanban_id>/<table>/<int:card_id>/<int:value>", methods=["GET", "POST"])
def progress_edit(kanban_id, table, card_id, value):
    card = ''

    if table == 'title_cards':
        card = TitleCard.query.get(card_id)
    elif table == 'title_text_cards':
        card = TitleTextCard.query.get(card_id)
    elif table == 'title_img_cards':
        card = TitleImgCard.query.get(card_id)

    if value != 10:
        value = -10
    card.progress += value

    if card.progress > 100:
        card.progress = 100
    elif card.progress < 0:
        card.progress = 0
    else:
        pass

    db.session.commit()

    return redirect(url_for('kanban', kanban_id=kanban_id))


@login_required
@app.route('/edit-kanban/<int:kanban_id>', methods=["GET", "POST"])
def edit_kanban(kanban_id):
    requested_kanban = KanbanTables.query.get(kanban_id)

    form = EditKanban(kanban_name=requested_kanban.kanban_name,
                      kanban_info=requested_kanban.kanban_info,
                      progress=requested_kanban.kanban_progress)

    if form.validate_on_submit():
        requested_kanban.kanban_name = form.kanban_name.data
        requested_kanban.kanban_info = form.kanban_info.data
        requested_kanban.kanban_progress = int(form.progress.data)

        db.session.commit()
        return redirect(url_for('kanban', kanban_id=kanban_id))

    return render_template("edit-kanban.html", form=form, kanban=requested_kanban)


if __name__ == '__main__':
    app.run(debug=True)
