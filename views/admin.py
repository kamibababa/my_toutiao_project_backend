import os
import uuid

import jwt

from flask import jsonify, request, send_from_directory
from functools import wraps

from mongoengine import Q

import config
from models import User, Channel, Img, Article, Cover
from werkzeug.security import generate_password_hash, check_password_hash

from app import app

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "Authorization" in request.headers:
            # Check whether token was sent
            authorization_header = request.headers["Authorization"]

            # Check whether token is valid
            try:
                token = authorization_header.split(" ")[1]
                user = jwt.decode(token, app.config["SECRET_KEY"])
            except:
                return jsonify({"error": "you are not logged in"}), 401

            return f(userid=user["userid"], *args, **kwargs)
        else:
            return jsonify({"error": "you are not logged in"}), 401
    return wrap

@app.route("/mp/v1_0/authorizations", methods=["POST"])
def login():
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


@app.route("/mp/v1_0/user/profile", methods=["GET"])
@login_required
def get_user_profile(userid):
    user = User.objects(id=userid).first()
    return jsonify({
        "message": 'OK',
        "data": user.to_public_json()
    })


@app.route("/mp/v1_0/channels", methods=["GET"])
@login_required
def get_channels(userid):
    # channel1 = Channel(
    #     name='python'
    # )
    # channel1.save()
    #
    # channel2 = Channel(
    #     name='java'
    # )
    # channel2.save()
    #
    # channel3 = Channel(
    #     name='mysql'
    # )
    # channel3.save()

    channels = Channel.objects()

    return jsonify({
        "message": 'OK',
        "data": {
            "channels": channels.to_public_json()
        }
    })

@app.route("/mp/v1_0/user/images", methods=["POST"])
@login_required
def upload(userid):
    user = User.objects(id=userid).first()
    image = request.files.get("image")
    if image:
        if not image.filename.endswith(tuple([".jpg", ".png"])):
            return jsonify({"error": "Image is not valid"}), 409

        # Generate random filename
        filename = str(uuid.uuid4()).replace("-", "") + "." + image.filename.split(".")[-1]

        if not os.path.isdir(config.image_upload_folder):
            os.makedirs(config.image_upload_folder)

        image.save(os.path.join(config.image_upload_folder, filename))
        img = Img(
            url=filename,
            user=user
        ).save()
    else:
        filename = None

    return jsonify({
        "message": 'OK',
        "data": img.to_public_json()
    })

@app.route("/file/<string:filename>")
def images_rsp(filename):
    return send_from_directory(config.image_upload_folder, filename)


# {"message": "OK", "data": {"id": 30840, "collect": true}}
@app.route("/mp/v1_0/user/images/<string:imageId>", methods=["PUT","DELETE"])
@login_required
def collectImage(userid,imageId):
    print(request.method)
    if request.method == 'PUT':
        img = Img.objects(id=imageId).first()
        img.is_collected = request.json.get('collect')
        img.save()
        return jsonify({
            "message": 'OK',
            "data": {
                "id": str(img.id),
                "collect": img.is_collected
            }
        })
    elif request.method == 'DELETE':
        img = Img.objects(id=imageId).first()
        img.delete()
        return jsonify({
            "message": 'OK',
            "data": {
                "id": str(img.id),
                "collect": img.is_collected
            }
        })

@app.route("/mp/v1_0/user/images")
@login_required
def get_images(userid):
    user = User.objects(id=userid).first()
    collect = request.args.get("collect")
    if collect == 'true':
        imgs = Img.objects(Q(user=user) & Q(is_collected=True))
    elif collect == 'false':
        imgs = Img.objects(user=user)

    page = int(request.args.get("page"))
    per_page = int(request.args.get("per_page"))

    paginated_imgs = imgs.skip((page - 1) * per_page).limit(per_page)

    return jsonify({
        "message": 'OK',
        "data": {
            "total_count": imgs.count(),
            "page": page,
            "per_page": per_page,
            "results": paginated_imgs.to_public_json()
        }
    })

@app.route("/mp/v1_0/articles", methods=["POST"])
@login_required
def addArticle(userid):
    user = User.objects(id=userid).first()

    draft = request.args.get('draft')
    if draft == "false":
        status = 2 #发布并审核通过
    else:
        status = 0 #草稿
    body = request.json
    print(draft)
    print(body)
    print(body["cover"])
    print(body.get("cover"))

    cover = Cover(
        type=body.get("cover")['type'],
        images=body.get("cover")['images']
    ).save()

    article = Article(
        title=body.get("title"),
        channel=body.get('channel_id'),
        content=body.get("content"),
        user=user,
        cover=cover,
        status=status,
    ).save()

    return jsonify({
        "message": 'OK',
        "data": {
        }
    })

@app.route("/mp/v1_0/articles", methods=["GET"])
@login_required
def getArticles(userid):
    user = User.objects(id=userid).first()
    page = int(request.args.get("page"))
    per_page = int(request.args.get("per_page"))
    status = None
    channel_id = None
    begin_pubdate = None
    end_pubdate = None
    if request.args.get("status") != None:
        status = int(request.args.get("status"))
    if request.args.get("channel_id") != None:
        channel_id = request.args.get("channel_id")
    if request.args.get("begin_pubdate") != None:
        begin_pubdate = request.args.get("begin_pubdate")
    if request.args.get("end_pubdate") != None:
        end_pubdate = request.args.get("end_pubdate")
    if begin_pubdate != None and channel_id != None and status != None:
        articles = Article.objects(user=user, status=status, channel=channel_id
                                   , created__gte=begin_pubdate, created__lte=end_pubdate)
    elif begin_pubdate != None and channel_id != None:
        articles = Article.objects(user=user, channel=channel_id
                                   , created__gte=begin_pubdate, created__lte=end_pubdate)
    elif begin_pubdate != None and status != None:
        articles = Article.objects(user=user, status=status
                                   , created__gte=begin_pubdate, created__lte=end_pubdate)
    elif status != None and channel_id != None:
        articles = Article.objects(user=user, status=status, channel=channel_id)
    elif status != None:
        articles = Article.objects(user=user, status=status)
    elif begin_pubdate != None:
        articles = Article.objects(user=user, created__gte=begin_pubdate, created__lte=end_pubdate)
    elif channel_id != None:
        articles = Article.objects(user=user,channel=channel_id)
    else:
        articles = Article.objects(user=user)

    paginated_articles = articles.skip((page - 1) * per_page).limit(per_page)

    return jsonify({
        "message": 'OK',
        "data": {
            "total_count": articles.count(),
            "page": page,
            "per_page": per_page,
            "results": paginated_articles.to_public_json()
        }
    })

@app.route("/mp/v1_0/articles/<string:article_id>", methods=["GET"])
@login_required
def getArticle(userid, article_id):
    article = Article.objects(id=article_id).first()
    return jsonify({
        "message": 'OK',
        "data": article.to_public_json_ex()
    })

@app.route("/mp/v1_0/articles/<string:article_id>", methods=["PUT"])
@login_required
def updateArticle(userid, article_id):
    user = User.objects(id=userid).first()
    draft = request.args.get('draft')
    if draft == "false":
        status = 2  # 发布并审核通过
    else:
        status = 0  # 草稿
    body = request.json

    channel_id = body.get('channel_id')
    channel = Channel.objects(id=channel_id).first()

    article = Article.objects(id=article_id).first()

    old_cover = article.cover
    old_cover.delete()

    cover = Cover(
        type=body.get("cover")['type'],
        images=body.get("cover")['images']
    ).save()

    article.title = body.get("title")
    article.channel = channel
    article.content = body.get("content")
    article.cover = cover
    article.status = status

    article.save()

    return jsonify({
        "message": 'OK',
        "data": {
        }
    })

@app.route("/mp/v1_0/articles/<string:article_id>", methods=["DELETE"])
@login_required
def deleteArticle(userid, article_id):
    article = Article.objects(id=article_id).first()
    old_cover = article.cover
    old_cover.delete()
    article.delete()
    return jsonify({
        "message": 'OK',
        "data": {}
    })