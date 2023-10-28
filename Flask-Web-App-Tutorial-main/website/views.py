from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from .models import Project
from flask_login import current_user
from flask import redirect, url_for
from flask import abort
from . import db
from flask import flash
import json
from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime


from .models import User, Note, Column, Task, Project, Category

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/new-project', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        title = request.form.get('title')
        new_project = Project(title=title, user_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('views.project_detail', project_id=new_project.id))
    return render_template('new_project.html')


@views.route('/projects')
@login_required
def projects():
    all_projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('projects.html', projects=all_projects, user=current_user)

@views.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

@views.route('/edit-project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        db.session.commit()
        return redirect(url_for('views.project_detail', project_id=project.id))

    return render_template('edit_project.html', project=project)


@views.route('/delete-project/<int:project_id>')
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('views.projects'))

@views.route('/add-column/<int:project_id>', methods=['POST'])
@login_required
def add_column(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)  # Forbidden access

    column_title = request.form.get('column_title')
    if column_title:
        new_column = Column(title=column_title, project_id=project.id)
        db.session.add(new_column)
        db.session.commit()

    return redirect(url_for('views.project_detail', project_id=project.id))



@views.route('/edit-column/<int:column_id>', methods=['GET', 'POST'])
@login_required
def edit_column(column_id):
    column = Column.query.get_or_404(column_id)
    
    # Ensure the user has permission to edit the column
    if column.project.user_id != current_user.id:
        abort(403)  # Forbidden access
    
    if request.method == 'POST':
        new_title = request.form.get('column_title')
        if new_title:
            column.title = new_title
            db.session.commit()
            return redirect(url_for('views.project_detail', project_id=column.project_id))
    
    return render_template('edit_column.html', column=column)


@views.route('/delete-column/<int:column_id>')
@login_required
def delete_column(column_id):
    column = Column.query.get_or_404(column_id)
    
    # Ensure the user has permission to delete the column
    if column.project.user_id != current_user.id:
        abort(403)  # Forbidden access
    
    db.session.delete(column)
    db.session.commit()
    return redirect(url_for('views.project_detail', project_id=column.project_id))

@views.route('/add-task/<int:column_id>', methods=['POST'])
@login_required
def add_task(column_id):
    column = Column.query.get_or_404(column_id)
    
    # Ensure the user has permission to add a task to the column
    if column.project.user_id != current_user.id:
        abort(403)  # Forbidden access

    # Extracting all task fields from the form data
    title = request.form.get('title')
    picture = request.form.get('picture')
    date = datetime.strptime(request.form.get('date'), "%Y-%m-%dT%H:%M")
    duration = int(request.form.get('duration'))
    pomodoros = int(request.form.get('pomodoros'))
    priority = request.form.get('priority')
    description = request.form.get('description')
    
    # Check if the category_id value is a number or a new category name
    category_id = request.form.get('category_id')
    if category_id:
        if category_id.isnumeric():
            category_id = int(category_id)
        else:
            # Here, category_id is actually a new category name.
            new_category = Category(name=category_id, user_id=current_user.id)
            db.session.add(new_category)
            db.session.commit()
            category_id = new_category.id
    else:
        category_id = None  # You can also set a default value if needed

    # Create a new task instance
    new_task = Task(
        title=title, 
        picture=picture, 
        date=date, 
        duration=duration, 
        pomodoros=pomodoros, 
        priority=priority, 
        category_id=category_id, 
        description=description, 
        column_id=column.id
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return redirect(url_for('views.project_detail', project_id=column.project_id))





@views.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    column = Column.query.get_or_404(task.column_id)
    project = Project.query.get_or_404(column.project_id)

    if project.user_id != current_user.id:
        abort(403)  # Forbidden access

    if request.method == 'POST':
        task.title = request.form.get('task_title')
        # Update other task details here

        db.session.commit()
        return redirect(url_for('views.project_detail', project_id=project.id))

    return render_template('edit_task.html', task=task)

@views.route('/delete-task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    column = Column.query.get_or_404(task.column_id)
    project = Project.query.get_or_404(column.project_id)

    if project.user_id != current_user.id:
        abort(403)  # Forbidden access

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('views.project_detail', project_id=project.id))


@views.route('/move-task', methods=['POST'])
@login_required
def move_task():
    task_id = request.form.get('task_id')
    new_column_id = request.form.get('new_column_id')

    # Ensure IDs are integers
    try:
        task_id = int(task_id)
        new_column_id = int(new_column_id)
    except ValueError:
        return jsonify(success=False, message="Invalid task or column ID"), 400

    task = Task.query.get(task_id)
    if not task:
        return jsonify(success=False, message=f"Task with ID {task_id} not found"), 404

    task.column_id = new_column_id

    try:
        db.session.commit()
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

    return jsonify(success=True)
  


@views.route('/task/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    column = Column.query.get(task.column_id)
    return render_template("task_detail.html", task=task, column=column)


def get_top_parent(task):
    """Recursively get the top parent of a task."""
    if task.parent_task_id:
        parent = Task.query.get(task.parent_task_id)
        return get_top_parent(parent)
    return task

@views.route('/task/<int:task_id>/add-subtask', methods=['POST'])
@login_required
def add_subtask(task_id):
    task = Task.query.get_or_404(task_id)
    
    subtask_title = request.form.get('subtask_title')
    if subtask_title:
        new_subtask = Task(title=subtask_title, parent_task_id=task.id)
        db.session.add(new_subtask)
        db.session.commit()
    
    # Get the top-most parent task
    top_parent = get_top_parent(task)
    
    # Redirect back to the top-most parent task's detail page
    return redirect(url_for('views.get_task', task_id=top_parent.id))
@views.route('/subtask/<int:subtask_id>/edit', methods=['POST'])
@login_required
def edit_subtask(subtask_id):
    subtask = Task.query.get_or_404(subtask_id)
    
    # Check if the subtask has an associated column and if the current user is authorized to edit the subtask
    if subtask.column and subtask.column.project.user_id != current_user.id:
        abort(403)  # Forbidden access

    new_title = request.form.get('new_title')
    if new_title:
        subtask.title = new_title
        db.session.commit()
        
        # Redirect back to the parent task's page after editing the subtask
        return redirect(url_for('views.get_task', task_id=subtask.parent_task_id))

    return jsonify({"error": "Invalid title"}), 400

@views.route('/subtask/<int:subtask_id>/delete', methods=['POST'])
@login_required
def delete_subtask(subtask_id):
    subtask = Task.query.get_or_404(subtask_id)

    # Check if the subtask has an associated column and if the current user is authorized to delete the subtask
    if subtask.column and subtask.column.project.user_id != current_user.id:
        abort(403)  # Forbidden access

    parent_task_id = subtask.parent_task_id
    db.session.delete(subtask)
    db.session.commit()

    # Redirect back to the parent task's page after deleting the subtask
    return redirect(url_for('views.get_task', task_id=parent_task_id))

@views.route('/move-subtask', methods=['POST'])
@login_required
def move_subtask():
    subtask_id = request.form.get('subtask_id')
    new_parent_id = request.form.get('new_parent_id')

    subtask = Task.query.get(subtask_id)
    if not subtask:
        return jsonify(success=False, message="Subtask not found"), 404

    subtask.parent_task_id = new_parent_id
    db.session.commit()

    return jsonify(success=True)

@views.route('/add-task-form/<int:column_id>', methods=['GET'])
@login_required
def add_task_form(column_id):
    column = Column.query.get_or_404(column_id)
    if column.project.user_id != current_user.id:
        abort(403)  # Forbidden access
    return render_template('add_task_form.html', column=column)

from flask import request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'static/uploads'  # Assuming you store uploaded images here
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/update-task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        flash("Task not found!", "error")
        return redirect(url_for('views.projects'))

    # Convert date string to datetime object
    date_str = request.form.get('date')
    task.date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")

    task.title = request.form.get('title')
    task.duration = int(request.form.get('duration'))
    task.pomodoros = int(request.form.get('pomodoros'))
    task.priority = request.form.get('priority')
    
    # Handle category_id
    category_id = request.form.get('category_id')
    if category_id and category_id.isnumeric():
        task.category_id = int(category_id)
    else:
        flash("Please provide a valid category.", "error")
        return redirect(url_for('views.edit_task', task_id=task.id))

    task.description = request.form.get('description')
    
    # Handle the image upload
    picture = request.files.get('picture')
    if picture and allowed_file(picture.filename):
        filename = secure_filename(picture.filename)
        picture.save(os.path.join(UPLOAD_FOLDER, filename))
        task.picture = filename

    try:
        db.session.commit()
        flash("Task updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating task: {str(e)}", "error")

    return redirect(url_for('views.project_detail', project_id=task.column.project_id))
