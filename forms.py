from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Optional


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    summary = StringField('Short Summary', validators=[Optional(), Length(max=300)])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[Optional()])
    tags = StringField('Tags (comma separated)', validators=[Optional(), Length(max=200)])
    image = FileField('Cover Image', validators=[
        Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    published = BooleanField('Publish immediately', default=True)
    submit = SubmitField('Save Post')
