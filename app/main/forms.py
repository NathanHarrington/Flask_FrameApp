from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from wtforms.validators import Email
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me',
                             validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CrawledForm(FlaskForm):
    vdtrs = [DataRequired()]

    ein_number = TextAreaField('EIN Number', validators=vdtrs)
    company_type = TextAreaField('Company Type', validators=vdtrs)
    certificate_type = TextAreaField('Certificate Type', validators=vdtrs)
    company_name = TextAreaField('Company Name', validators=vdtrs)
    street_address = TextAreaField('Street Address', validators=vdtrs)
    city = TextAreaField('City', validators=vdtrs)
    state = TextAreaField('State', validators=vdtrs)
    zip_code = TextAreaField('ZipCode', validators=vdtrs)
    phone = TextAreaField('phone', validators=vdtrs)
    submit = SubmitField('Submit')

class SubscriberForm(FlaskForm):
    vdtrs = [DataRequired(), Email()]

    email = StringField('Email Address', validators=vdtrs)
    submit = SubmitField('Sign up')
