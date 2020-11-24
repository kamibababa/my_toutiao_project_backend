import jwt

from flask import jsonify, request
from functools import wraps
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

from app import app

#

@app.route("/mp/v1_0/authorizations", methods=["POST"])
def login():
    # hashed_password = generate_password_hash('246810')
    # User(
    #     mobile='13911111111',
    #     code=hashed_password,
    #     photo='http://toutiao-img.itheima.net/FuyELvGh8jbise6dfoEr0W7luPLq',
    #     gender=1,
    #     name='zhangsan',
    #     intro='zhangsanfeng'
    # ).save()

    if not request.json.get("mobile"):
        return jsonify({"error": "mobile not specified"}), 409
    if not request.json.get("code"):
        return jsonify({"error": "code not specified"}), 409

    try:
        mobile = request.json.get("mobile")
        print(mobile)
        users = User.objects(mobile=mobile)
    except:
        print('error')

    user = users.first()

    if user == None:
        return jsonify({"error": "User not found"}), 403


    if not check_password_hash(user.code, request.json.get("code")):
        return jsonify({"error": "Invalid password"}), 401

    # token = jwt.encode({
    #     "userid": str(user.id),
    #     "username": user.username,
    #     "email": user.email,
    #     "password": user.password,
    #     "created": str(user.created)
    # }, app.config["SECRET_KEY"])

    return jsonify({
        "message": 'OK',
        "data": {
            "user": user.name,
            "token": "xxxxxxxxxxxxxxxx",
        }
    })