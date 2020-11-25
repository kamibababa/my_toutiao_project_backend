import datetime

from mongoengine import *

connect("yesterday_toutiao")

class User(Document):
    mobile = StringField(max_length=11, unique=True)
    name = StringField(required=True, unique=True)
    code = StringField(required=True)
    created = DateTimeField(required=True, default=datetime.datetime.now())
    photo = StringField(required=True)
    gender = IntField(required=True)
    intro = StringField(required=True)
    email = StringField(required=True, unique=True)

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
