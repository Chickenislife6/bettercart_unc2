
        
import json
import time
from datareq.datatypes.Creds import Creds
from unc import SignUpHelper
from flask import Flask, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app, max_age=86400)
print("test")

@app.route("/", methods = ['GET', 'POST'])
def hello():
    if request.method == 'GET':
        return "HELLO WORLD!"
    if request.method == 'POST':
        actions = request.form.get('ACTIONS')
        print(actions)
        return actions
    return "Hello World!"

@app.route("/api/lookup", methods = ['POST'])
def lookup():
    user = request.form.get('USER')
    password = request.form.get('PASSWORD')
    classes = request.form.get('CLASSES').split()
    cred = Creds(user, password)
    instance = SignUpHelper.try_login(cred)
    classes = instance.check_class(classes)
    result = {}
    for elt in classes:
        result[elt[1]] = elt[0]
    return json.dumps(result)

@app.route("/api/add", methods = ['POST'])
def add():
    user = request.form.get('USER')
    password = request.form.get('PASSWORD')
    classes = request.form.get('CLASSES').split()
    cred = Creds(user, password)
    instance = SignUpHelper.try_login(cred)
    class_list = instance.setup_cart()

    indices = [False for _ in range(len(class_list))]
    for elt in class_list.items():
        if str(elt[0]) in classes:
            indices[elt[1]] = True

    if request.form.get('TIME'):
        a = time.time()
        while a - int(request.form.get('TIME')) < 0: # time has not been reached yet, loop
            a = time.time()
            time.sleep(0.1)
            
    result = instance.register_in_classes(indices)
    return result

@app.route("/api/swap", methods = ['POST'])
def swap():
    user = request.form.get('USER')
    password = request.form.get('PASSWORD')
    classes = request.form.get('CLASSES').split()
    cred = Creds(user, password)
    instance = SignUpHelper.try_login(cred)

    if request.form.get('TIME'):
        a = time.time()
        while a - int(request.form.get('TIME')) < 0: # time has not been reached yet, loop
            a = time.time()
            time.sleep(0.1)

    result = instance.swap(classes[0], classes[1])
    return result



if __name__ == "__main__":
    app.run(debug=True)

