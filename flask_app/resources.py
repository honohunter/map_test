from flask_app import app
from flask_restful import Resource, reqparse, fields, marshal_with
from flask_app.models import UserModel, RevokedTokenModel, LocationModel
import flask_jwt_extended as jwt


class SignUp(Resource):

    def post(self):
        """
               This function responds to Sign Up request for '/signup' with reqparse parameters
               :param username:     String
               :param password:     String
               :return:             200 on success with an object {msg:String}

        """

        # Get parameters from the request
        parser = reqparse.RequestParser()
        parser.add_argument('username', help='This field cannot be blank', required=True)
        parser.add_argument('password', help='This field cannot be blank', required=True)
        data = parser.parse_args()
        # Query the database for existing username
        if UserModel.find_by_username(data['username']):
            return {'msg': 'User {} already exists'.format(data['username'])}
        # If not try to create username with a hashed password
        new_user = UserModel(username=data['username'], password=UserModel.generate_hash(data['password']))
        try:
            # Save the username/password
            new_user.save_to_db()
            return {
                'msg': 'User {} was created'.format(data['username']),
            }
        except:
            return {'msg': 'Something went wrong'}, 500


class Login(Resource):

    def post(self):

        """
            This function responds to Sign Up request for '/login'  with reqparse parameters
            :param username:     String
            :param password:     String
            :return:             200 on success with an object
                                {
                                    msg:String,
                                    access_token:String, 15 minute session
                                    refresh_token:String , 30 days session
                                }

        """
        # Get parameters from the request
        parser = reqparse.RequestParser()
        parser.add_argument('username', help='This field cannot be blank', required=True)
        parser.add_argument('password', help='This field cannot be blank', required=True)
        data = parser.parse_args()
        try:
            # Query the database for existing username
            current_user = UserModel.find_by_username(data['username'])
            if not current_user:
                return {'msg': 'User {} doesnt exist'.format(data['username'])}
            # Verify if the hashed password in true and return jwt tokens
            if UserModel.verify_hash(data['password'], current_user.password):
                access_token = jwt.create_access_token(identity=data['username'])
                refresh_token = jwt.create_refresh_token(identity=data['username'])
                return {
                    'msg': 'Logged in as {}'.format(current_user.username),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            else:
                return {'msg': 'Wrong credentials'}
        except:
            return {'msg': 'Something went wrong'}, 500


class LogoutAccess(Resource):

    @jwt.jwt_required
    def post(self):
        """
            This function responds to Sign Up request for '/login'  with reqparse parameters
            :param username:     String
            :param password:     String
            :return:             200 on success with an object {msg:String, access_token:String, refresh_token:String}

        """
        jti = jwt.get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'msg': 'Access token has been revoked'}
        except:
            return {'msg': 'Something went wrong'}, 500


class LogoutRefresh(Resource):
    @jwt.jwt_refresh_token_required
    def post(self):
        jti = jwt.get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'msg': 'Refresh token has been revoked'}
        except:
            return {'msg': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt.jwt_refresh_token_required
    def post(self):
        current_user = jwt.get_jwt_identity()
        access_token = jwt.create_access_token(identity=current_user)
        return {'access_token': access_token}


class UserLocation(Resource):
    resource_fields = {
        'location_id': fields.Integer,
        'lon': fields.String,
        'lat': fields.String,
        'comments': fields.String
    }

    @staticmethod
    def current_user_id():
        current_user = UserModel.find_by_username(jwt.get_jwt_identity())
        return current_user.user_id

    @jwt.jwt_required
    @marshal_with(resource_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('lon', help='This field cannot be blank', required=True)
        parser.add_argument('lat', help='This field cannot be blank', required=True)
        parser.add_argument('comments', help='This field cannot be blank')
        data = parser.parse_args()
        new_location = LocationModel(user_id=self.current_user_id(), lon=data['lon'], lat=data['lat'],
                                     comments=data['comments'])

        try:
            new_location.save_to_db()
            return new_location
        except:
            return {'msg': 'Something went wrong'}, 500

    @jwt.jwt_required
    @marshal_with(resource_fields)
    def get(self):
        try:
            return LocationModel.read_from_db(self.current_user_id())
        except:
            return {'msg': 'Something went wrong'}, 500

    @jwt.jwt_required
    @marshal_with(resource_fields)
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('location_id', help='This field cannot be blank', required=True)
        parser.add_argument('lon', help='This field cannot be blank', required=True)
        parser.add_argument('lat', help='This field cannot be blank', required=True)
        parser.add_argument('comments', help='This field cannot be blank')
        data = parser.parse_args()
        update_location = LocationModel.get_by_location_id(data['location_id'])

        update_location.lon = data['lon']
        update_location.lat = data['lat']
        update_location.comments = data['comments']

        try:
            update_location.update_to_db()
            return update_location
        except:
            return {'msg': 'Something went wrong'}, 500

    @jwt.jwt_required
    @marshal_with(resource_fields)
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('location_id', help='This field cannot be blank', required=True)
        data = parser.parse_args()

        delete_location = LocationModel.get_by_location_id(data['location_id'])

        try:
            delete_location.delete_from_db()
            return delete_location
        except:
            return {'msg': 'Something went wrong'}, 500


class SecretResource(Resource):
    resource_fields = {
        'user_id': fields.Integer,
        'username': fields.String
    }

    # @jwt.jwt_required
    # @marshal_with(resource_fields)
    # def get(self):
    #     current_user = jwt.get_jwt_identity()
    #     return UserModel.find_by_username(current_user)


if __name__ == '__main__':
    app.run(debug=True)
