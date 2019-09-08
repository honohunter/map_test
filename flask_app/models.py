from flask_app import db, ma
from marshmallow import fields
from passlib.hash import pbkdf2_sha256 as sha256


class UserModel(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    locations = db.relationship('LocationModel', backref='user')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class LocationModel(db.Model):
    __tablename__ = 'location'
    location_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.user_id'))
    lon = db.Column(db.Float())
    lat = db.Column(db.Float())
    comments = db.Column(db.String())

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_to_db(self):
        db.session.merge(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def read_from_db(cls, user_id):
        return cls.query.join(UserModel).filter(UserModel.user_id == user_id).all()

    @classmethod
    def get_by_location_id(cls, location_id):
        return cls.query.filter(cls.location_id == location_id).one_or_none()


# class UserModelSchema(ma.ModelSchema):
#     class Meta:
#         model = UserModel
#         sqla_session = db.session
#
#     # locations = fields.Nested('UserLocationModelSchema', default=[], many=True)


# class UserLocationModelSchema(ma.ModelSchema):
#     user_id = fields.Int()
#     location_id = fields.Int()
#     comments = fields.Str()


# class LocationModelSchema(ma.ModelSchema):
#     class Meta:
#         model = LocationModel
#         sqla_session = db.session
#
#     # user = fields.Nested('LocationUserModelSchema', default=[], many=True)


# class LocationUserModelSchema(ma.ModelSchema):
#     user_id = fields.Int()
#     username = fields.Str()


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String())

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
