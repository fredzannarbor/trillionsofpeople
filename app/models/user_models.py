# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>
import flask
from flask import Flask, redirect, render_template, request, url_for
from flask_user import UserMixin
# from flask_user.forms import RegisterForm
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import MultipleFileField
from wtforms import StringField, SubmitField, validators, TextAreaField, SelectField, RadioField
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func
app = Flask(__name__)
db = SQLAlchemy()
db.init_app(app)

# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    # reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    #created_on = db.Column(db.DateTime, default=func.now(), nullable=False)

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))

    def has_role(self, role):
        return role in self.roles

# Stripe Customer data model

class StripeCustomer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    stripeCustomerId = db.Column(db.String(255), nullable=False)
    stripeSubscriptionId = db.Column(db.String(255), nullable=False)


# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


# Define the User profile form
class UserProfileForm(FlaskForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')

# Define the User prompt form
class UserPromptForm(FlaskForm):
    user_prompt = StringField('', validators=[
        validators.DataRequired('A prompt is required'), validators.length(max=100)])
    submit = SubmitField('Submit')

class NoUserInput(FlaskForm):
    submit = SubmitField('Submit')

class Bot(FlaskForm):
    user_prompt = StringField('', validators=[
        validators.DataRequired('A prompt is required'), validators.length(max=100)])
    submit = SubmitField('Submit')

class BookPromptForm(FlaskForm):
    user_prompt = StringField('User prompt', validators=[
        validators.DataRequired('A prompt is required'), validators.length(max=100)])
    submit = SubmitField('Submit')

class UserDocsForm(FlaskForm):
    radiobuttons = RadioField()
    submit = SubmitField('Submit')

class LoadMyDocsForm(FlaskForm):
    file = FileField()
    answerstitle = StringField('Title', validators=[validators.DataRequired('Title is required'), validators.length(max=255)])
    answersauthor = StringField('Author', validators=[validators.DataRequired('Author is required'), validators.length(max=255)])
    answersbuyurl = StringField('Buy URI', validators=[validators.DataRequired('Buy URI is required'), validators.length(max=255)])
    answersimageurl = StringField('Image URI', validators=[validators.DataRequired('Image URI is required'), validators.length(max=255)])
    submit = SubmitField("Load to OpenAI")

class ShareMyDocsForm(FlaskForm):
    selectedbook = SelectField(
        'Select a book', coerce=int, validators=[validators.DataRequired('Book must be selected')])
    user_prompt = StringField('', validators=[
        validators.DataRequired('A prompt is required'), validators.length(max=100)])
    submit = SubmitField("Load to OpenAI")

def find_or_create_userdocs(user_id, userdoc_filename):
    """ Find existing customer or create new prompt """
    userdocs = UserDocs.query.filter(UserDocs.user_id == user_id)

    if userdocs:
        userdocs = UserDocs(user_id=user_id,
        userdoc_filename=userdoc_filename)
        db.session.add(userdocs)
        db.session.commit()
     
    else:
        pass
    return userdocs

def find_or_create_searchdocs(user_id, searchhandle):
    """ Find existing search handle """
    searchdoc = SearchDocs.query.filter(SearchDocs.user_id == user_id)

    if searchdoc:
        searchhandle = searchhandle.id
        print(searchhandle)
        searchdocs = SearchDocs(user_id=user_id,
        searchhandle=searchhandle)

        db.session.add(searchdocs)
        db.session.commit()
     
    else:
        print('no document found, error')
    return searchdocs

def find_or_create_answersdocs(user_id, answershandle):
    """ Find existing answers handle """
    answersdoc = AnswersDocs.query.filter(SearchDocs.user_id == user_id)

    if answersdoc:
        answersdocs = AnswersDocs(user_id=user_id,
        answershandle=answershandle)

        db.session.add(answersdocs)
        db.session.commit()
     
    else:
        print('no document found, error')
    return answersdocs



class UserTextArea(FlaskForm):
    user_text_area = TextAreaField('Enter description of your book here', render_kw={'class': 'form-control', 'rows': 7}, validators=[
        validators.DataRequired('A prompt is required'), validators.length(max=500)])
    submit = SubmitField('Submit')

# define the Admin prompt form

class AdminPromptForm(FlaskForm):
    admin_prompt = TextAreaField('Admin prompt', validators=[
        validators.DataRequired('A prompt is required'), validators.length(max=1000)])
    submit = SubmitField('Submit')

class DropdownApps(FlaskForm):
    language = SelectField(
        'Select an application',
        choices=[('keywords', 'Keywords'), ('BISAC', 'BISAC Codes'), ('copy', 'Cover Copy')]
    )

class Presets(db.Model):
    __tablename__ = 'presets'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    preset_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    preset_author = db.Column(db.String(255), nullable=False)
    preset_instructions = db.Column(db.String(255), nullable=False)
    preset_author = db.Column(db.String(255), nullable=False)
    preset_description = db.Column(db.String(255), nullable=False)

    @classmethod
    def get_elements(cls):
        presets = Preset.query.all()
        return presets
    
    @classmethod
    def get_sorted_by(presets, sort, reverse=False):
        return sorted(
            presets.get_elements(),
            key=lambda x: getattr(x, sort),
            reverse=reverse)

    @classmethod
    def get_element_by_id(presets, id):
        return [i for i in presets.get_elements() if i.id == id][0]

class Tokens(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    totaltokens = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime, default=func.now(), nullable=False)

class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    totaltokens = db.Column(db.String(255), nullable=False)
    pre_user_input = db.Column(db.Text, nullable=True)
    user_input = db.Column(db.Text, nullable=True)
    post_user_input = db.Column(db.Text, nullable=True)
    prompt = db.Column(db.Text, nullable=True)
    engine = db.Column(db.Text, nullable=True)
    response = db.Column(db.Text, nullable=True)
    safety_rating = db.Column(db.Integer, nullable=True)
    created_on = db.Column(db.DateTime, default=func.now(), nullable=False)

class UserDocs(db.Model):
    __tablename__ = 'userdocs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    userdoc_filename = db.Column(db.String(255), nullable=False)

class SearchDocs(db.Model):
    __tablename__ = 'searchdocs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    searchhandle = db.Column(db.String(255), nullable=False)

class AnswersDocs(db.Model):
    __tablename__ = 'answersdocs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    answershandle = db.Column(db.String(255), nullable=False)
    answerstitle = db.Column(db.String(255), nullable=False)
    answersauthor = db.Column(db.String(255), nullable=False)
    answersbuyurl = db.Column(db.String(255), nullable=True)
    answersimageurl = db.Column(db.String(255), nullable=True)

class Journals(db.Model):
    __tablename__ = 'journals'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    journal_text = db.Column(db.Text, nullable=False)
    created_on = db.Column(db.Text , nullable=False)
