import os
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from flask_cors import CORS
from models import db, User, Project, Task

app = Flask(__name__)
os.makedirs("instance", exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
app.config['JWT_SECRET_KEY'] = 'secretkey'

db.init_app(app)

jwt = JWTManager(app)
CORS(app)

# CREATE DATABASE
with app.app_context():
    db.create_all()


# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['POST'])
def register():

    data = request.json

    username = data['username']
    email = data['email']
    password = data['password']
    role = data.get('role', 'member')

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    user = User(
        username=username,
        email=email,
        role=role
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'})


# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['POST'])
def login():

    data = request.json

    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        'token': token,
        'role': user.role
    })


# ---------------- CREATE PROJECT ---------------- #

@app.route('/projects', methods=['POST'])
@jwt_required()
def create_project():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if user.role != 'admin':
      return jsonify({'message': 'Admin only'}), 403
    data = request.json

    project = Project(
        name=data['name'],
        description=data['description']
    )

    db.session.add(project)
    db.session.commit()

    return jsonify({'message': 'Project created'})


# ---------------- GET PROJECTS ---------------- #

@app.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():

    projects = Project.query.all()

    result = []

    for p in projects:
        result.append({
            'id': p.id,
            'name': p.name,
            'description': p.description
        })

    return jsonify(result)


# ---------------- CREATE TASK ---------------- #

# ---------------- CREATE TASK ---------------- #

@app.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'message':'Admin only'}),403

    data = request.json

    task = Task(

        title=data['title'],
        description=data['description'],
        status=data['status'],
        due_date=data['due_date'],
        user_id=data['user_id'],
        project_id=data['project_id']
    )

    db.session.add(task)

    db.session.commit()

    return jsonify({'message':'Task created'})


# ---------------- GET TASKS ---------------- #

@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():

    tasks = Task.query.all()

    result = []

    for t in tasks:

        result.append({

            'id':t.id,
            'title':t.title,
            'description':t.description,
            'status':t.status,
            'due_date':t.due_date,
            'assigned_to':t.assigned_user.username if t.assigned_user else '',
            'project':t.project.name if t.project else ''

        })

    return jsonify(result)

# ---------------- UPDATE TASK STATUS ---------------- #

# ---------------- UPDATE TASK STATUS ---------------- #

@app.route('/tasks/<int:id>', methods=['PUT'])
@jwt_required()
def update_task(id):

    data = request.json

    task = Task.query.get(id)

    if not task:
        return jsonify({'message':'Task not found'}),404

    task.status = data['status']

    db.session.commit()

    return jsonify({'message':'Task updated'})
@app.route("/")
def home():
    return "Team Task Manager backend running Sucessfully "
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
