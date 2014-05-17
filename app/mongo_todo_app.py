import sys
import ast
from bson import json_util, ObjectId
from flask import Flask, jsonify, abort, make_response, request, json
from flask.ext.pymongo import PyMongo
from flask.ext.httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

# assumes name of your app for db unless you pass in other
app = Flask(__name__)
mongo = PyMongo(app)


@app.route('/')
@auth.get_password
def get_password(username):
    """
    callback in HTTPBasicAuth extension that gets the password
    for a given user
    """
    if username == 'foo':
        return 'bar'
    return None


@auth.error_handler
def unauthorized():
    """
    callback in HTTPBasicAuth extension when unauthorized error code
    occurs and is sent back to client
    """
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route('/todo/api/v1/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    """
    Retrieves all tasks' titles from todo collection in app_mongo db
    Uses json.dumps to convert BSON to JSON (serialization) taking
    @default param: json_util.default
    Alternatively we could use bson.json_util dumps instead which
    handles binary and code data structures - but more recurssion = slower
    and is unnecessary for our little todo api
    http://api.mongodb.org/python/current/api/bson/json_util.html

    To retrieve all tasks in our todo list use curl:

    curl -u foo:bar -i http://localhost:5000/todo/api/v1/tasks
    or check it out at in your browser at: http://localhost:5000/todo/api/v1/tasks
    """
    tasks_list = iterate_cursor()
    return jsonify({'tasks': tasks_list})


@app.route('/todo/api/v1/tasks/<ObjectId:task_id>', methods=['GET'])
def get_task(task_id):
    """
    get request for a single task that matches
    task_id to current id and returns matching task

    curl -i http://localhost:5000/todo/api/v1.0/tasks/<ObjectId:task_id>

    Where <ObjectId:task_id> is mongodb "_id" which is assigned
    when you import your todo.json by mongodb
    """

    task_list = iterate_cursor()

    # build list comprehension to return matching item in request from db
    task = [item_id for item_id in task_list if item_id['_id']
            ['$oid'] == str(task_id)]

    if len(task) == 0:  # error if no match to task
        abort(404)

    return jsonify({'task': task[0]})   # returns matched task


@app.route('/todo/api/v1/tasks', methods=['POST'])
def create_task():
    """
    post method to create a new task
    insert into mongo collection and returns
    json object by grabbing the last inserted document
    from collection
    """

    task = {
        '_id': ObjectId(),
        'description': request.get_json()['description'],
        'title': request.get_json()['title'],
        'done': "False"
    }

    mongo.db.todo.insert(task)
    new_task = serialize_json(task)
    return jsonify({'task': new_task}), 201


@app.route('/todo/api/v1/tasks/<ObjectId:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Updates a single task in mongo database matching _id
    passed in URI returns a jsonify'd object
    Test with curl where ObjectId is the mongodb "_id":

    curl -i -H "Content-Type: application/json" -X PUT -d "{\"done\":\"True\"}" http://localhost:5000/todo/api/v1/tasks/<ObjectId:task_id>
    """

    # pymongo find_one grabs single matching document searching by _id
    task_dict = mongo.db.todo.find_one({"_id": ObjectId(task_id)})

    if len(task_dict) == 0:
        abort(404)
    if not request.get_json:
        abort(400)

    # update task attributes
    task_dict['title'] = request.get_json('title', task_dict['title'])
    task_dict['description'] = request.get_json(
        'description', task_dict['description'])
    task_dict['done'] = request.get_json('done', task_dict['description'])

    # update todo collection from http request
    if 'title' in request.get_json() & type(request.get_json()) == str:
        mongo.db.todo.update(
            {'_id': task_dict['_id']}, {'$set': task_dict['title']})
    if 'description' in request.get_json():
        mongo.db.todo.update(
            {'_id': task_dict['_id']}, {'$set': task_dict['description']})
    if 'done' in request.get_json() & type(request.get_json()) == str:
        mongo.db.todo.update(
            {'_id': task_dict['_id']}, {'$set': task_dict['done']})
    else:
        abort(404)

    # get updated data from mongodb
    task_list = iterate_cursor()
    return jsonify({'task': task_list})


@app.route('/todo/api/v1/tasks/<ObjectId:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Gets the task based on it's _id that is passed into the URI via curl
    using pyMongo's find_one (in the terminal it's findOne)
    """

    task_dict = mongo.db.todo.find_one({"_id": ObjectId(task_id)})

    if len(task_dict) == 0:
        abort(404)

    mongo.db.todo.remove(task_dict)
    return jsonify({'result': True})


def iterate_cursor():
    """
    Creates a mongodb cursor object using find()
    and iterates over documents in the todo collection
    then convert the bson to json, returning a list
    """
    try:
        cursor = mongo.db.todo.find()
    except:
        print "error", sys.exc_info()[0]

    # iterate over mongodb cursor
    todo_list = [i for i in cursor]
    return serialize_json(todo_list)


def serialize_json(task):
    """
    Handles serializing the json converting it from a
    bson object to a json object to expose the list to
    user as json. returns list
    """
    serialize_json = json.dumps(task, default=json_util.default)
    # convert string to list
    new_task = ast.literal_eval(serialize_json)
    return new_task


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
