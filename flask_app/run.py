from flask_app import run, api, app, jwt
from flask_app import resources, models, views


api.add_resource(resources.SignUp, '/signup')
api.add_resource(resources.Login, '/login')
api.add_resource(resources.LogoutAccess, '/logout/access')
api.add_resource(resources.LogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.UserLocation, '/location')
api.add_resource(resources.SecretResource, '/secret')


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


if __name__ == '__main__':
    app.run(debug=True)
