import os
import uuid

import jwt

from flask import jsonify, request, send_from_directory

from mongoengine import Q

import config
from models import User, Channel, Img, Article, Cover
from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from .common import login_required


@app.route("/app/v1_0/authorizations", methods=["POST"])
def app_login():
    # hashed_password = generate_password_hash('246810')
    # User(
    #     mobile='13911111111',
    #     code=hashed_password,
    #     photo='http://toutiao-img.itheima.net/FuyELvGh8jbise6dfoEr0W7luPLq',
    #     gender=1,
    #     name='zhangsan',
    #     intro='zhangsanfeng',
    #     email='zhangsan@qq.com'
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

    token = jwt.encode({
        "userid": str(user.id),
        "name": user.name,
        "email": user.email,
        "created": str(user.created)
    }, app.config["SECRET_KEY"]).decode('utf-8')

    return jsonify({
        "message": 'OK',
        "data": {
            "user": user.name,
            "token": token,
        }
    })

# {
# 	"message": "OK",
# 	"data": {
# 		"name": "13911111116",
# 		"photo": "http://toutiao-img.itheima.net/Fkj6tQi3xJwVXi1u2swCElotfdCi",
# 		"is_media": false,
# 		"intro": "",
# 		"certi": "",
# 		"art_count": 0,
# 		"follow_count": 2,
# 		"fans_count": 0,
# 		"like_count": -4,
# 		"id": 1159803119077425152
# 	}
# }

@app.route("/app/v1_0/user", methods=["GET"])
@login_required
def get_user_info(userid):
    userinfo = User.objects(id=userid).first()
    if not userinfo:
        return jsonify({"message": "Invalid user."})
    else:
        return jsonify({
            "message": 'OK',
            "data": {
                "name": userinfo.name,
                "photo": userinfo.photo,
                "is_media": False,
                "intro": userinfo.intro,
                "certi": "",
                "art_count": 5,
                "follow_count": 5,
                "fans_count": 5,
                "like_count": 5,
                "id": str(userinfo.id)
            }
        })
@app.route("/app/v1_0/channels", methods=["GET"])
@login_required
def client_get_channels(userid):

    channels = Channel.objects()

    return jsonify({
        "message": 'OK',
        "data": {
            "channels": channels.to_public_json()
        }
    })

@app.route("/app/v1_0/user/channels", methods=["PATCH"])
@login_required
def user_add_channel(userid):
    user = User.objects(id=userid).first()
    body = request.json
    channels = body.get('channels')
    channel_id = channels[0]['id']
    channel_add = Channel.objects(id=channel_id).first()
    user.channels.append(channel_add)
    user.save()
    return jsonify({
        "message": 'OK',
        "data": {}
    })

@app.route("/app/v1_0/user/channels", methods=["GET"])
@login_required
def get_user_channels(userid):
    user = User.objects(id=userid).first()

    return jsonify({
        "message": 'OK',
        "data": {
            "channels":[channel.to_public_json() for channel in user.channels]
        }
    })

@app.route("/app/v1_0/user/channels/<string:channelid>", methods=["DELETE"])
@login_required
def delete_user_channel(userid,channelid):
    user = User.objects(id=userid).first()
    channel_del = Channel.objects(id=channelid).first()
    user.channels.remove(channel_del)
    user.save()

    return jsonify({
        "message": 'OK',
        "data": {}
    })