from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import InputRequired, NoneOf


class PromptForm(FlaskForm):
    prompt_text = StringField('Prompt',
                              validators=[InputRequired(), NoneOf([])])
    submit = SubmitField('Ask something')


class AddFileForm(FlaskForm):
    document = FileField('File', validators=[InputRequired(), NoneOf([])])
    submit = SubmitField('Add file')
