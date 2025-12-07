from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Student
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'students.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create db if not exists
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    students = Student.query.order_by(Student.id.desc()).all()
    return render_template('index.html', students=students)


@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        course = request.form.get('course', '').strip()
        age = request.form.get('age', '').strip()

        # Basic validation
        if not name or not email:
            flash('Name and Email are required.', 'danger')
            return redirect(url_for('add_student'))

        # convert age
        try:
            age_val = int(age) if age else None
        except ValueError:
            flash('Age must be an integer.', 'danger')
            return redirect(url_for('add_student'))

        # check unique email
        if Student.query.filter_by(email=email).first():
            flash('A student with that email already exists.', 'danger')
            return redirect(url_for('add_student'))

        student = Student(name=name, email=email, course=course or None, age=age_val)
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('add_student.html')


@app.route('/student/<int:student_id>')
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('view_student.html', student=student)


@app.route('/student/<int:student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        course = request.form.get('course', '').strip()
        age = request.form.get('age', '').strip()

        if not name or not email:
            flash('Name and Email are required.', 'danger')
            return redirect(url_for('edit_student', student_id=student.id))

        try:
            age_val = int(age) if age else None
        except ValueError:
            flash('Age must be an integer.', 'danger')
            return redirect(url_for('edit_student', student_id=student.id))

        # if email changed, ensure unique
        if email != student.email and Student.query.filter_by(email=email).first():
            flash('A different student already uses that email.', 'danger')
            return redirect(url_for('edit_student', student_id=student.id))

        student.name = name
        student.email = email
        student.course = course or None
        student.age = age_val

        db.session.commit()
        flash('Student updated successfully.', 'success')
        return redirect(url_for('view_student', student_id=student.id))

    return render_template('edit_student.html', student=student)


@app.route('/student/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)