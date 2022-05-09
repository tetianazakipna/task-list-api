import re
from turtle import title
from flask import Blueprint, jsonify, abort, make_response, request
from sqlalchemy import false
from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# helper functions
def validate_task(task_id):
    try:
        task_id = int(task_id)
    except: 
        abort(make_response({"details": f"task id '{task_id}' is invalid. Task id should be a number."}, 400))
    task = Task.query.get(task_id)
    if not task:
        abort(make_response({"details": f"task with task id {task_id} is not found"}, 404))
    return task 

def task_dictionary(task):
    return {
        "task": {
            "id":task.task_id,
            "title":task.title,
            "description":task.description,
            "is_complete": False
        }
    }

# route functions
@tasks_bp.route("", methods=["POST"])
def add_one_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body:
        return jsonify({"details": "Invalid data"}), 400
    new_task = Task(title=request_body["title"],
                    description=request_body["description"])

    db.session.add(new_task)
    db.session.commit()

    return task_dictionary(new_task), 201

@tasks_bp.route("", methods=["GET"])
def get_all_tasks():
    params = request.args
    if "sort" in params and params["sort"] == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif "sort" in params and params["sort"] == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
    task_response = []
    for task in tasks:
        task_response.append({
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        })
    return jsonify(task_response), 200

@tasks_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    task = validate_task(task_id)
    return task_dictionary(task), 200

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_one_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body:
        return jsonify({"details": f"Request must include title and description"}), 400
    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()
    return task_dictionary(task), 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_one_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'details':f'Task {task_id} "{task.title}" successfully deleted'}), 200
