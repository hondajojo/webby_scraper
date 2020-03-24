from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, RadioField, SelectField
from wtforms.validators import DataRequired


class AddConfigForm(FlaskForm):
    source = SelectField(u'source', choices=[('craigslist', 'source(craigslist)'),
                                             ('facebook', 'source(facebook)'),
                                             ('ebay', 'source(ebay)'),
                                             ('kijiji', 'source(kijiji)')])
    url = StringField(u'url', validators=[DataRequired()])
    active = RadioField('active', choices=[("1", 'active'), ("0", 'inactive')])
    # spider_ip = StringField(u'spider_ip', validators=[DataRequired(), IPAddress()])
    submit = SubmitField('Submit')


class AddKeywordsFilterForm(FlaskForm):
    keywords = StringField(u'keywords')
    submit = SubmitField('Submit')
