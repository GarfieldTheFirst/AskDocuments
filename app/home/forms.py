from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, NoneOf


class PromptForm(FlaskForm):
    prompt_text = StringField('Prompt',
                              validators=[InputRequired(), NoneOf([])])
    submit = SubmitField('Ask something')
