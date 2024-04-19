from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Date
from flask_bootstrap import Bootstrap5
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = "adasdadvsvbgh"
bootstrap = Bootstrap5(app)


# ---------------- SECTION DB ----------------
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

today = datetime.today()


class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created: Mapped[Date] = mapped_column(Date, nullable=False)
    due_date: Mapped[Date] = mapped_column(Date, nullable=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


class TaskForm(FlaskForm):
    name = StringField('Název', default='Úkol')
    created = DateField('Vytvořeno', default=today)
    text = TextAreaField('Text', validators=[DataRequired()])
    due_date = DateField('Termín', default=today)
    status = SelectField('Status',
                         choices=[('In Progress', 'In Progress'), ('Completed', 'Completed')], )
    Potvrdit = SubmitField()


@app.route("/", methods=(["GET", "POST"]))
def home():
    form = TaskForm()
    result = db.session.execute(db.select(Task).order_by(Task.id))
    data = result.scalars().all()
    print(type((data[0].due_date)))
    print(type(today))


    if request.method == "POST" and form.validate_on_submit():
        # print("Validation passed.")
        data = request.form
        new_entry = Task(
            name=form.name.data,
            created=form.created.data,
            due_date=form.due_date.data,
            text=form.text.data,
            status=form.status.data
        )

        db.session.add(new_entry)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("index.html", data=data, form=form, today=today.date())



@app.route("/delete")
def delete():
    task_id = request.args.get('id')
    task = db.get_or_404(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/done")
def done():
    task_id = request.args.get('id')
    task_to_update = db.get_or_404(Task, task_id)
    task_to_update.status = 'Completed'
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    task_id = request.args.get('id')
    device = db.get_or_404(Task, task_id)
    form = TaskForm(obj=device)
    if form.validate_on_submit():
        print("POST metoda:")
        form.populate_obj(device)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
