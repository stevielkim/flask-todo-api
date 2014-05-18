##Small todo API project using Flask and MongoDB

####app_mongo.py is a very simple API for a todo list in Flask and MongoDB.

#####mongo_todo_app.py inspired by Miguel Grinbergs tutorial at http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

To get started first create a virtual environment:
```
virtualenv -p python2.7 todo_venv
```

Then activate your virtual environment
```
source todo_venv/bin/activate
```

Next you'll need to install Flask, PyMongo, Flask-HTTPAuth
```
pip install Flask
pip install Flask-PyMongo
pip install flask-httpauth
```

And you can follow MongoDB's installation guidelines http://docs.mongodb.org/manual/installation/ on their site.  I use homebrew myself which, if you use install via this formula name:
```
brew install mongodb
```

###Start your mongodb instance follow the directions via:
```
brew info mongodb
```

Where there will be the directions at the bottom to either start the Mongo server using launchctl or simply type:
```
mongod
```

Then open another tab and start the mongo shell:
```
mongo
```

So lets import our data, create our database and our todo collection in one go with the mongodb import statement
If you run into any issues here is the Mongo help page on imports
http://docs.mongodb.org/manual/reference/program/mongoimport/
```
mongoimport -d mongo_todo_app -c todo < todo.json
```
Where this points to our mongo_todo_app database and creates the todo collection on the fly. Notice a couple of things - our database is the same name as our app since we passed in __name__ (which refers to the app name) into Flask in the mongo_todo_app. If you want to change the name to something else you can by passing in a different name, and again if you run into any problems check out the docs at https://flask-pymongo.readthedocs.org/en/latest/
The other thing to note is when we import our data if the collecton already exists the import statement will append the data to the current documents in our collection (it doesn't replace the data, it inserts more data into the collection).


###The app
Alright now we have a working mongodb database called mongo_todo_app and a todo collection with three items in it.
Move to the app folder and open the mongo_todo_app.py file.  Here you'll find all the details about each of the functions used for our CRUD todo API including the curl commands you'll use to test each http request.

To run the app just cd into the app folder and run the mongo_todo_app.py file
```
python mongo_todo_app.py
```

Then open a new tab in your terminal and (making sure your still in you virtual environment) start playing around with the curl commands you find in mongo_todo_app.py file or in your browser: http://localhost:5000/todo/api/v1/tasks

Note: Only the getTasks() function has authentication
