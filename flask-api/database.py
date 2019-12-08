from pymongo import MongoClient
from bson import Decimal128, ObjectId


class DataSource:
    def __init__(self, config):
        self.connection = MongoClient(config.get('MONGODB_URI'))
        self.items = self.connection[config.get('MONGODB_DATABASE')][config.get('MONGODB_COLLECTION')]

    def get_categorias(self):
        """
        Retorna todas as categorias de produtos das ofertas salvas no banco
        """
        categorias = self.items.distinct('categoria')
        return [categoria for categoria in categorias if categoria is not None]

    def get_num_ofertas(self):
        """
        Retorna o número total de ofertas no banco
        """
        ofertas = self.items.estimated_document_count()
        return ofertas

    def get_oferta(self, _id):
        """
        Retorna toda informação sobre uma oferta específica, dado um id
        """
        oferta = self.items.find_one({'_id': ObjectId(_id)}, projection={'_id': False})
        return oferta

    def get_ofertas_por_titulo(self, titulo, limite: int, offset: int):
        """
        Retorna todas as ofertas que correspondam ao titulo (ou fragmento de titulo) passado
        """
        ofertas = self.items.find({'titulo': {'$regex': titulo, '$options': 'i'}},
                                  projection={'titulo': True,
                                              'moeda': True,
                                              'preco': True,
                                              'disponivel': True}, skip=offset, limit=limite)
        resultado = []
        for oferta in ofertas:
            resultado.append(oferta)
        return resultado

    def get_ofertas_por_faixa_de_preco(self, pmin, pmax, limite: int, offset: int):
        """
        Retorna todas as ofertas que correspondam à faixa de preço passada [pmin, pmax]
        """
        ofertas = self.items.find({'preco': {'$gte': Decimal128(pmin), '$lte': Decimal128(pmax)}},
                                  projection={'titulo': True,
                                              'moeda': True,
                                              'preco': True,
                                              'disponivel': True}, skip=offset, limit=limite)
        resultado = []
        for oferta in ofertas:
            resultado.append(oferta)
        return resultado
