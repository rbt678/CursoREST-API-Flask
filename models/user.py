from sql_alchemy import banco

class UserModel(banco.Model):
    __tablename__ = 'usuarios'
    
    user_id = banco.Column(banco.Integer, primary_key=True)
    login = banco.Column(banco.String(40))
    senha = banco.Column(banco.String(40))
    ativado = banco.Column(banco.Boolean, default=False)
    
    def __init__(self, login, senha, ativado):
        self.login = login
        self.senha = senha
        self.ativado = ativado

    def json(self):
        return {
            'login': self.login,
            'senha': self.senha,
            'ativado': self.ativado
        }
    
    @classmethod
    def find_user(cls, user_id):
        if user:= cls.query.filter_by(user_id=user_id).first():
            return user
        return None
    
    @classmethod
    def find_by_login(cls, login):
        if user:= cls.query.filter_by(login=login).first():
            return user
        return None
    
    def save_user(self):
        banco.session.add(self)
        banco.session.commit()
        
    def update_user(self, login, senha):
        self.__init__(login, senha)
        
    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()