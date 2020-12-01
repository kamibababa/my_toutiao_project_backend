import datetime
import time

from mongoengine import *

import config

connect("yesterday_toutiao")

class CustomQuerySet(QuerySet):
    def to_public_json(self):
        result = []
        try:
            for doc in self:
                jsonDic = doc.to_public_json()
                result.append(jsonDic)
        except:
            print('error')

        return result

class Channel(Document):
    name = StringField(max_length=120, required=True)

    meta = {'queryset_class': CustomQuerySet}

    def to_public_json(self):
        data = {
            "id": str(self.id),
            "name": self.name,
        }
        return data

class User(Document):
    mobile = StringField(max_length=11, unique=True)
    name = StringField(required=True, unique=True)
    code = StringField(required=True)
    created = DateTimeField(required=True, default=datetime.datetime.now())
    photo = StringField(required=True)
    gender = IntField(required=True)
    intro = StringField(required=True)
    email = StringField(required=True, unique=True)
    channels = ListField(ReferenceField(Channel))

    def to_public_json(self):
        data = {
            "mobile":self.mobile,
            "name": self.name,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
            "photo": self.photo,
            "gender": self.gender,
            "intro": self.intro,
            "email": self.email
        }

        return data


class Cover(Document):
    type = IntField(required=True)
    images = ListField(StringField(max_length=200))

    def to_public_json(self):
        data = {
            "images": self.images,
            "type": self.type
        }
        return data


class Article(Document):
    title = StringField(max_length=120, required=True)
    content = StringField(max_length=10000)
    channel = ReferenceField(Channel, reverse_delete_rule=CASCADE)
    cover = ReferenceField(Cover)
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    created = DateTimeField(required=True, default=datetime.datetime.now())
    status = IntField(required=True)

    meta = {'queryset_class': CustomQuerySet}

    def to_public_json(self):
        data = {
            "id": str(self.id),
            "status": self.status,
            "title" : self.title,
            "pubdate":self.created,
            "cover":self.cover.to_public_json()
        }
        return data

    def to_public_json_ex(self):
        data = {
            "id": str(self.id),
            "title" : self.title,
            "content": self.content,
            "channel_id":str(self.channel.id),
            "cover":self.cover.to_public_json()
        }
        return data

class Img(Document):
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    url = StringField(max_length=200, required=True)
    is_collected = BooleanField(required=True,default=False)

    meta = {'queryset_class': CustomQuerySet}

    def to_public_json(self):
        data = {
            "id": str(self.id),
            "url": config.base_url + self.url,
            "is_collected" : self.is_collected
        }
        return data

# 1589337751688

# 1606806890174
# 1606620445458
# if __name__ == '__main__':
    # article = Article.objects().first()
    #
    # millisec = article.created.timestamp() * 1000
    # print(int(millisec))


    # d = datetime.datetime.fromtimestamp(1606620445458 / 1000)
    # # 精确到毫秒
    # print(d)
    # print(type(d))
    # str1 = d.strftime("%Y-%m-%d %H:%M:%S.%f")
    # print(str1)  # 2019-10-11 14:15:56.514000


    # channel = Channel.objects(id='5fbf2345d757c18a921094b9').first()
    # user = User.objects().first()
    # cover = Cover.objects().first()
    # for i in range(33):
    #     time.sleep(1)
    #     print(i)
    #     article = Article(
    #         title=f"ArticleArticleArticle{i}",
    #         channel=channel,
    #         content=f"ArticleArticleArticlecontentcontentcontent{i}",
    #         user=user,
    #         cover=cover,
    #         status=2,
    #         created=datetime.datetime.now()
    #     ).save()
