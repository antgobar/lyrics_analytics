from wtforms import Form, BooleanField, StringField, validators


class SearchForm(Form):
    name = StringField('Artist name', [validators.Length(min=1, max=30)])
