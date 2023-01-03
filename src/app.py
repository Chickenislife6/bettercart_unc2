import json
import time
from datareq.datatypes.Creds import Creds
from flask import Flask, request
from flask_cors import CORS
from flask_cors import cross_origin
from database.database import get_redis, store_data
from functions.signupclass import SessionWrapper
from functions import check_class, getsubject, register, swapclasses
from functions.attribute_to_description import translate

import os, psutil
process = psutil.Process(os.getpid())

app = Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"
app.config["CACHE_TYPE"] = "null"

@app.route("/", methods=["GET", "POST"])
@cross_origin()
def hello():
    if request.method == "GET":
        return f"HELLO WORLD! {process.memory_info().rss}"
    if request.method == "POST":
        actions = request.form.get("ACTIONS")
        print(actions)
        return actions
    return "Hello World!"

@app.route("/api/lookup_subject", methods=["POST"])
@cross_origin()
# @store_data
def lookup_subject():
    user = request.form.get("USER")
    password = request.form.get("PASSWORD")
    subject = request.form.get("SUBJECT")
    attribute = request.form.get("ATTRIBUTE")
    cred = Creds(user, password)
    instance = SessionWrapper.try_login(cred)
    d = getsubject.get_cart(instance, subject, False, attribute)
    d.update(getsubject.get_cart(instance, subject, True, attribute))
    return json.dumps(d)

@app.route("/api/guest/lookup_subject", methods=["POST", "GET"])
@cross_origin()
def lookup_subject_guest():
    subject = request.form.get("SUBJECT", default="")
    attribute = request.form.get("ATTRIBUTE", default="")

    r = get_redis()
    result = {}

    for key in r.keys():
        value = r.get(key)
        if translate(attribute) in value and subject in value:
            
            result[key] = value.split("~")[:-1]
    
    return json.dumps(result)


## depreciated!!
@app.route("/api/lookup", methods=["POST"])
@cross_origin()
def lookup():
    user = request.form.get("USER")
    password = request.form.get("PASSWORD")
    classes = request.form.get("CLASSES").split()
    cred = Creds(user, password)
    instance = SessionWrapper.try_login(cred)
    classes = check_class.check_class(instance, classes)
    result = {}
    for elt in classes:
        result[elt[1]] = elt[0]
    return json.dumps(result)


@app.route("/api/add", methods=["POST"])
@cross_origin()
def add():
    user = request.form.get("USER")
    password = request.form.get("PASSWORD")
    classes = request.form.get("CLASSES").split()
    cred = Creds(user, password)
    instance = SessionWrapper.try_login(cred)
    class_list = instance.setup_cart()

    indices = [False for _ in range(len(class_list))]
    for elt in class_list.items():
        if str(elt[0]) in classes:
            indices[elt[1]] = True

    if request.form.get("TIME"):
        a = time.time()
        while (
            a - int(request.form.get("TIME")) < 0
        ):  # time has not been reached yet, loop
            a = time.time()
            time.sleep(0.05)

    result = register.register_in_classes(instance, indices)
    return result


@app.route("/api/swap", methods=["POST"])
@cross_origin()
def swapclasses():
    user = request.form.get("USER")
    password = request.form.get("PASSWORD")
    classes = request.form.get("CLASSES").split()
    cred = Creds(user, password)
    instance = SessionWrapper.try_login(cred)

    if request.form.get("TIME"):
        a = time.time()
        while (
            a - int(request.form.get("TIME")) < 0
        ):  # time has not been reached yet, loop
            a = time.time()
            time.sleep(0.1)

    result = swapclasses.swap(instance, classes[0], classes[1])
    return result


@app.route("/api/verify", methods=["POST"])
@cross_origin()
def verify():
    user = request.form.get("USER")
    password = request.form.get("PASSWORD")
    cred = Creds(user, password)
    instance = SessionWrapper.try_login(cred)
    return instance



if __name__ == "__main__":
    CORS(app, max_age=86400)
    app.run()
