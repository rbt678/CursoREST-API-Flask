from flask import Flask
from flask_restful import  Api
from flask_jwt_extended import JWTManager
from resources.hotel import Hoteis, Hotel, HoteisCadastrar
from resources.user import Users, User, UserRegistro, UserLogin, UserLogout
from blacklist import BLACKLIST

BLACKLIST=set()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'NotTellingYou'
app.config['JWT_BLACKLIST_ENABLED'] = True
api = Api(app)
jwt = JWTManager(app)

@app.before_request
def cria_banco():
    banco.create_all()
    
@jwt.token_in_blocklist_loader
def verifica_blacklist(self, token):
    return token['jti'] in BLACKLIST

@jwt.revoked_token_loader
def token_de_acesso_invalidado(jwt_header, jwt_payload):
    return {'message': 'token de acesso invalidado'}, 401

api.add_resource(Hoteis, '/hoteis')
api.add_resource(HoteisCadastrar, '/cadastrar-hoteis')
api.add_resource(Hotel, '/hoteis/<hotel_id>')
api.add_resource(Users, '/users')
api.add_resource(User, '/users/<user_id>')
api.add_resource(UserRegistro, '/cadastro')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')

if __name__ == '__main__':
    from sql_alchemy import banco
    banco.init_app(app)
    app.run(debug=True)