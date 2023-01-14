from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, SelectField, DecimalField, URLField
from wtforms.validators import DataRequired, URL, InputRequired, NumberRange
from wtforms.widgets import TextArea

class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()],
                       render_kw={"placeholder": "Your Email", 'class': 'inputfield'})
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"placeholder": "Password", 'class': 'inputfield'})
    name = StringField("Your Name", validators=[DataRequired()],
                       render_kw={"placeholder": "Your Name", 'class': 'inputfield'})
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()],
                       render_kw={"placeholder": "Your Email", 'class': 'inputfield'})
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"placeholder": "Password", 'class': 'inputfield'})
    submit = SubmitField("Log In")


class NewKanbanForm(FlaskForm):
    kanban_name = StringField("Your Name", validators=[DataRequired()],
                              render_kw={"placeholder": "Your Kanban Name", 'class': 'inputfield'})
    kanban_info = StringField("Your Info", widget=TextArea(), validators=[DataRequired()],
                              render_kw={"placeholder": "Some info about the Kanban", 'class': 'inputfieldtext'})
    submit = SubmitField("Save")


class NewTitleCard(FlaskForm):
    card_title = StringField("Card's Name", validators=[DataRequired()],
                             render_kw={"placeholder": "Card Title", 'class': 'inputfield'})
    submit = SubmitField("Save")


class NewTextCard(FlaskForm):
    text_card_title = StringField("Card's Name", validators=[DataRequired()],
                                  render_kw={"placeholder": "Card Title", 'class': 'inputfield'})
    card_text = StringField("Text", widget=TextArea(), validators=[DataRequired()],
                            render_kw={"placeholder": "Card Text", 'class': 'inputfieldtext'})
    submit = SubmitField("Save")


class NewImgCard(FlaskForm):
    img_card_title = StringField("Card's Name", validators=[DataRequired()],
                                 render_kw={"placeholder": "Card Title", 'class': 'inputfield'})
    card_img_url = URLField("Image URL", validators=[DataRequired()],
                            render_kw={"placeholder": "Card Image (URL)", 'class': 'inputfield'})
    submit = SubmitField("Save")


class EditCard(FlaskForm):
    card_title_edited = StringField("Card's Name", validators=[DataRequired()],
                                    render_kw={"placeholder": "Card Title", 'class': 'inputfield'})
    card_text_edited = StringField("Text", widget=TextArea(),
                                   render_kw={"placeholder": "Card Text", 'class': 'inputfieldtext'})
    card_img_url_edited = URLField("Image URL",
                                   render_kw={"placeholder": "Card Image (URL)", 'class': 'inputfield '})
    position = SelectField(u'Programming Language', choices=[('0', 'Backlog'), ('1', 'In Progress'), ('2', 'In Review'), ('3', 'Completed')])
    progress = DecimalField('Card Progress', places=0, validators=[NumberRange(min=0, max=100,
                                                                               message='Use a number between 1 and 100.')])
    submit = SubmitField("Save")

class EditKanban(FlaskForm):
    kanban_name = StringField("Kanban's Name", validators=[DataRequired()],
                              render_kw={"placeholder": "Kanban Name", 'class': 'inputfield'})
    kanban_info = StringField("Kanban Info", widget=TextArea(),
                              render_kw={"placeholder": "Kanban Text", 'class': 'inputfieldtext'})
    progress = DecimalField('Kanban Progress', places=0, validators=[NumberRange(min=0, max=100,
                                                                                 message='Use a number between 1 and 100.')])

    submit = SubmitField("Save")

