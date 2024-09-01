from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from hmac import compare_digest
from models.user import UserModel
from blacklist import BLACKLIST

class Users(Resource):
    def get(self):
        return {'usuarios': [usuario.json() for usuario in UserModel.query.all()]}


class User(Resource):
    def mensagem_retorno(return_code, usuario=None):
        if return_code == 1:
            return {'message': 'usuario não encontrado'}, 404
        if return_code == 2:
            return {'message': 'usuario já existe'}, 400
        if return_code == 3:
            return {'message': 'usuario adicionado com sucesso', 'novo_usuario': usuario}, 201
        if return_code == 4:
            return {'message': 'usuario atualizado com sucesso', 'novo_usuario': usuario}, 200
        if return_code == 5:
            return {'message': 'usuario removido com sucesso', 'usuario_removido': usuario}, 200
        if return_code == 6:
            return {'message': 'login ou senha invalidos'}, 401
        if return_code == 7:
            return {'message': 'usuario não ativado'}, 400
        if return_code == 8:
            return {'message': f'usuario {usuario} ativado com sucesso'}, 200
        if return_code == 9:
            return {'message': 'deslogado com sucesso'}, 200
                
        raise 'Codigo de retorno desconhecido'
    
    def get(self, user_id):
        if user := UserModel.find_user(user_id):
            return user.json()
        return User.mensagem_retorno(1)
    
    @jwt_required()
    def delete(self, user_id):
        if user := UserModel.find_user(user_id):
            try:
                user.delete_user()
            except:
                return {'message': 'ocorreu um erro interno'}, 500
            return User.mensagem_retorno(5, user.json())
        return User.mensagem_retorno(1)
    
class UserRegistro(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('login', type=str, required=True, help='login do usuario obrigatório')
    parser.add_argument('senha', type=str, required=True, help='senha do usuario obrigatório')
    parser.add_argument('ativado', type=bool)
    
    def post(self):
        args=UserRegistro.parser.parse_args()
        if UserModel.find_by_login(args['login']):
            return User.mensagem_retorno(2)
        
        user=UserModel(**args)
        user.ativado = False
        user.save_user()
        return User.mensagem_retorno(3, user.json())
    
class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('login', type=str, required=True, help='login do usuario obrigatório')
    parser.add_argument('senha', type=str, required=True, help='senha do usuario obrigatório')
    
    def post(self):
        args = UserLogin.parser.parse_args()
        user = UserModel.find_by_login(args['login'])
        
        if user and compare_digest(user.senha, args['senha']):
            if user.ativado:
                return {'token': create_access_token(identity=user.user_id)}, 200
            return User.mensagem_retorno(7)
        
        return User.mensagem_retorno(6)
    
class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLACKLIST.add(jti)
        return User.mensagem_retorno(9)
    
class UserConfirmar(Resource):
    
    @classmethod
    def get(cls, user_id):
        if not (user:=UserModel.find_user(user_id)):
            return User.mensagem_retorno(1)
        
        user.ativado = True
        user.save_user()
        return User.mensagem_retorno(8, user.json().get('login'))
        