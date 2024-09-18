from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, DateField, StringField, PasswordField, EmailField, FileField
from wtforms.validators import DataRequired

from utils import COUNTRY_CHOICES


GENDER_CHOICES = [
    ('F', 'Жіноча'),
    ('M', 'Чоловіча'),
]

ENTRY_CHOICES = [
    ('1', 'Один раз'),
    ('2', 'Два рази'),
    ('MULT', 'Багаторазова')
]

TYPE_CHOICES = [
    ('Employment', 'Тип для працевлаштування'),
    ('Business', 'Тип для бізнесу'),
    ('Tourist', 'Туристичний тип'),
    ('Student', 'Студентський тип'),
    ('Transit', 'Транзитний тип'),
]


class SignUpForm(FlaskForm):
    name = StringField('Ім’я:', validators=[DataRequired()])
    surname = StringField('Прізвище:', validators=[DataRequired()])
    patronymic = StringField('По батькові:', validators=[DataRequired()])
    email = EmailField('Електронна пошта:', validators=[DataRequired()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    re_password = PasswordField('Повторіть пароль:', validators=[DataRequired()])
    sex = SelectField('Стать:', choices=GENDER_CHOICES, validators=[DataRequired()])
    date_of_birth = DateField('Дата народження:', validators=[DataRequired()])
    place_of_birth = StringField('Місце народження:', validators=[DataRequired()])
    nationality = SelectField('Громадянство:', choices=COUNTRY_CHOICES, validators=[DataRequired()])
    submit = SubmitField('Зареєструватися')


class LoginForm(FlaskForm):
    email = EmailField('Електронна пошта:', validators=[DataRequired()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    submit = SubmitField('Увійти')


class ExtendVisaForm(FlaskForm):
    reason = StringField('Причина подовження:', validators=[DataRequired()])
    extension_date = DateField('Бажана дата подовження:', validators=[DataRequired()])
    submit = SubmitField('Надіслати')


class RestoreVisaForm(FlaskForm):
    photo = FileField('Фото для відновлення візи:', validators=[DataRequired()])
    submit = SubmitField('Надіслати')


class CreateVisaForm(FlaskForm):
    type = SelectField('Тип візи:', choices=TYPE_CHOICES, validators=[DataRequired()])
    country = SelectField('Країна:', choices=COUNTRY_CHOICES, validators=[DataRequired()])
    entry_amount = SelectField('Кількість в`їздів:', choices=ENTRY_CHOICES, validators=[DataRequired()])
    photo = FileField('Фото:', validators=[DataRequired()])
    submit = SubmitField('Створити')


class ComleteTaskForm(FlaskForm):
    place_of_issue = StringField('Місце видачі:', validators=[DataRequired()])
    date_of_issue = DateField('Дата видачі:', validators=[DataRequired()])
    date_of_expiry = DateField('Дійсний до:', validators=[DataRequired()])
    submit = SubmitField('Відправити')
