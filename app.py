# app.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///countries_states.db'

db = SQLAlchemy(app)


# Database Models
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    states = db.relationship('State', backref='country', lazy=True)

    def __repr__(self):
        return f"Country('{self.name}')"


class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)

    def __repr__(self):
        return f"State('{self.name}')"


# WTForm for state selection
class StateForm(FlaskForm):
    country = SelectField('Country', coerce=int)
    state = SelectField('State', coerce=int)
    submit = SubmitField('Submit')


# WTForm for multiplication
class MultiplicationForm(FlaskForm):
    num1 = StringField('Number 1', validators=[DataRequired()])
    num2 = StringField('Number 2', validators=[DataRequired()])
    submit = SubmitField('Calculate')


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/state', methods=['GET', 'POST'])
def state():
    form = StateForm()
    
    # Fetch countries and populate the country dropdown
    countries = Country.query.all()
    form.country.choices = [(country.id, country.name) for country in countries]

    # Populate states based on selected country
    if form.validate_on_submit():
        country_id = form.country.data
        states = State.query.filter_by(country_id=country_id).all()
        form.state.choices = [(state.id, state.name) for state in states]
        state_name = State.query.get(form.state.data).name
        return render_template('state.html', state=state_name)
    
    return render_template('state_dropdown.html', form=form)


@app.route('/multiplication', methods=['GET', 'POST'])
def multiplication():
    form = MultiplicationForm()
    if form.validate_on_submit():
        num1 = int(form.num1.data)
        num2 = int(form.num2.data)
        result = num1 * num2
        return render_template('multiplication_result.html', result=result)
    return render_template('multiplication_form.html', form=form)


# Ensure that db.create_all() is executed within the application context
with app.app_context():
    db.create_all()

    # Insert sample data into the Country and State tables
    if not Country.query.filter_by(name='USA').first():
        usa = Country(name='USA')
        db.session.add(usa)
        db.session.commit()

        ny = State(name='New York', country=usa)
        ca = State(name='California', country=usa)
        db.session.add(ny)
        db.session.add(ca)
        db.session.commit()

    if not Country.query.filter_by(name='Canada').first():
        canada = Country(name='Canada')
        db.session.add(canada)
        db.session.commit()

        on = State(name='Ontario', country=canada)
        qc = State(name='Quebec', country=canada)
        db.session.add(on)
        db.session.add(qc)
        db.session.commit()


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
