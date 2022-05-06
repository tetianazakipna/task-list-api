from operator import ne
from flask import Blueprint, jsonify, request, make_response, abort

from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body:
        return jsonify({"details": f"Invalid data"}), 400

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"]
    )
    
    db.session.add(new_task)
    db.session.commit()

    return{
        "task":{
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": False
        }
    }, 201

@tasks_bp.route("", methods=["GET"])
def get_all_tasks():
    params = request.args

    if "sort" in params:
        if params["sort"] == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all()
        else:
            tasks = Task.query.order_by(Task.title).all()
    else:
        tasks = Task.query.all()
        
    response = []
    for task in tasks:
        response.append(
            {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False  
            }
        )
    return jsonify(response), 200

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        abort(make_response({"details": f"Invalid task id '{task_id}'. Task id expected to be a number."}, 400))
    
    task = Task.query.get(task_id)

    if not task:
        abort(make_response({"details": f"No task with id '{task_id}' found."}, 404))
    
    return task

@tasks_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    task = validate_task(task_id)
    return {
        "task":{
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False 
        }
    }, 200

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_one_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body:
        return jsonify({"details": f"Request to update must include title and description"}), 400
    
    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return {
        "task":{
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False 
        }
    }, 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = validate_task(task_id)

    db.session.delete(task)
    db.session.commit()

    return make_response(jsonify({'details': f'Task {task_id} "{task.title}" successfully deleted'}), 200)

