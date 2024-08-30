from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from flask import request
from models.hotel import HotelModel
import sqlite3


class Hoteis(Resource):
    path_parser = reqparse.RequestParser()
    path_parser.add_argument('cidade', type=str)
    path_parser.add_argument('estrelas_min', type=float)
    path_parser.add_argument('estrelas_max', type=float)
    path_parser.add_argument('diaria_min', type=float)
    path_parser.add_argument('diaria_max', type=float)
    path_parser.add_argument('limit', type=int)
    path_parser.add_argument('offset', type=int)
    
    def normaliza_path_parametros(cidade=None, estrelas_min=0, estrelas_max=5, diaria_min=0, diaria_max=1000, limit=50, offset=0, **dados):
        parametros = {'estrelas_min': estrelas_min, 'estrelas_max': estrelas_max, 'diaria_min': diaria_min, 'diaria_max': diaria_max, 'limit': limit, 'offset': offset}
        if cidade:
            parametros['cidade'] = cidade
        return parametros
    
    def get(self):
        connection = sqlite3.connect('instance/banco.db')
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        dados = Hoteis.path_parser.parse_args()
        dados_validos = {chave: dados[chave] for chave in dados if dados[chave] is not None}
        parametros_normalizados = Hoteis.normaliza_path_parametros(**dados_validos)
        consulta = f'''SELECT * FROM hoteis WHERE {'cidade = ? AND ' if parametros_normalizados.get('cidade') else ''}estrelas >= ? AND estrelas <= ? AND diaria >= ? AND diaria <= ? LIMIT ? OFFSET ?'''
        tupla_consulta = ((parametros_normalizados.get('cidade'),) if parametros_normalizados.get('cidade')else()) +(parametros_normalizados['estrelas_min'], parametros_normalizados['estrelas_max'], parametros_normalizados['diaria_min'], parametros_normalizados['diaria_max'], parametros_normalizados['limit'], parametros_normalizados['offset'])
        print('TESTE')
        print(tupla_consulta)
        resultado = cursor.execute(consulta, tupla_consulta)
        return {'hoteis': [dict(hotel) for hotel in resultado.fetchall()]}


class Hotel(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('nome', type=str, required=True, help='nome do hotel obrigatório')
    parser.add_argument('estrelas', type=float, required=True, help='estrelas do hotel obrigatório')
    parser.add_argument('diaria', type=float, required=True, help='diaria do hotel obrigatório')
    parser.add_argument('cidade', type=str, required=True, help='cidade do hotel obrigatório')
            
    def mensagem_retorno(return_code, hotel=None):
        if return_code == 1:
            return {'message': 'hotel não encontrado'}, 404
        if return_code == 2:
            return {'message': 'hotel já existe'}, 400
        if return_code == 3:
            return {'message': 'hotel adicionado com sucesso', 'novo_hotel': hotel}, 201
        if return_code == 4:
            return {'message': 'hotel atualizado com sucesso', 'novo_hotel': hotel}, 200
        if return_code == 5:
            return {'message': 'hotel removido com sucesso', 'hotel_removido': hotel}, 200
        
        raise 'Codigo de retorno desconhecido'
    
    def get(self, hotel_id):
        if hotel := HotelModel.find_hotel(hotel_id):
            return hotel.json()
        return Hotel.mensagem_retorno(1)
    
    @jwt_required()
    def post(self, hotel_id, pular=False):
        if not pular and HotelModel.find_hotel(hotel_id):
            return Hotel.mensagem_retorno(2)
        
        args = Hotel.parser.parse_args()
        novo_hotel = HotelModel(hotel_id, **args)
        try:
            novo_hotel.save_hotel()
        except:
            return {'message': 'ocorreu um erro interno'}, 500
        
        return Hotel.mensagem_retorno(3, novo_hotel.json())
    
    @jwt_required()
    def put(self, hotel_id):
        if hotel:=HotelModel.find_hotel(hotel_id):
            args = Hotel.parser.parse_args()
            hotel.update_hotel(**args)
            try:
                hotel.save_hotel()
            except:
                return {'message': 'ocorreu um erro interno'}, 500
            return Hotel.mensagem_retorno(4, hotel.json())
        
        return Hotel.post(self, hotel_id, pular=True)
    
    @jwt_required()
    def delete(self, hotel_id):
        if hotel := HotelModel.find_hotel(hotel_id):
            try:
                hotel.delete_hotel()
            except:
                return {'message': 'ocorreu um erro interno'}, 500
            return Hotel.mensagem_retorno(5, hotel.json())
        return Hotel.mensagem_retorno(1)
    
class HoteisCadastrar(Resource):
    def post(self):
        # Acessando o corpo da requisição diretamente como JSON
        data = request.get_json()

        # Verificando se o dado é uma lista de dicionários
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # Processa cada dicionário aqui
                    hotel_id = item.get('hotel_id')
                    nome = item.get('nome')
                    estrelas = item.get('estrelas')
                    diaria = item.get('diaria')
                    cidade = item.get('cidade')   
                    
                    hotel = HotelModel(hotel_id, nome, estrelas, diaria, cidade)
                    hotel.save_hotel()
                else:
                    return {"error": "Each item in the list must be a dictionary"}, 400
            return {"message": "Data processed successfully"}, 200
        else:
            return {"error": "Request body must be a list of dictionaries"}, 400
            
        