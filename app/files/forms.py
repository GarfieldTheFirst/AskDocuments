from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField
from wtforms.validators import InputRequired, NoneOf


class AddFileForm(FlaskForm):
    document = FileField('File', validators=[InputRequired(), NoneOf([])])
    submit = SubmitField('Add file')
