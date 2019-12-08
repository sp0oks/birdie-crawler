from flask import Flask, jsonify, request, url_for

from database import DataSource

server = Flask(__name__)
server.config.from_object('config.Config')
server.db = DataSource(server.config)

HEADERS = {'Access-Control-Allow-Origin': '*'}


@server.route('/', methods=['GET'])
def index():
    
    msg = 'Bem vindo! ' \
          'Esta API pode ser usada para consultar ofertas coletadas de sites populares de venda como Magazine Luiza, Mercado Livre e Casas Bahia.'
    info = {'Ofertas disponíveis': server.db.get_num_ofertas(),
            'Categorias de produtos disponíveis': server.db.get_categorias(),
            'Endpoints': {'/oferta/<id>': 'retorna informações sobre uma oferta específica',
                          '/ofertas/<titulo>': 'retorna resultado de pesquisa sobre um titulo ou parte de titulo',
                          '/ofertas/<preco_minimo>-<preco_maximo>': 'retorna resultado de pesquisa sobre uma faixa de precos'}}
          
    return jsonify(msg=msg, info=info), 200, HEADERS


@server.route('/oferta/<_id>', methods=['GET'])
def oferta(_id):
    """
    Rota para informações sobre um produto específico por id
    """
    status = 204
    produto = server.db.get_oferta(_id)
    if produto:
        status = 200
        produto['preco'] = str(produto['preco'])

    return jsonify(oferta=produto), status, HEADERS


@server.route('/ofertas/titulo/<titulo>', methods=['GET'])
def busca_titulo(titulo):
    """
    Rota para busca de ofertas por titulo (ou parte de título) do produto
    """
    limite = request.args.get('limite') or 30
    offset = request.args.get('offset') or 0
    
    if isinstance(limite, str):
        limite = int(limite)
    if isinstance(offset, str):
        offset = int(offset)

    msg = {}
    paginas = {'anterior': None, 'proximo': None}
    status = 204
    
    msg['ofertas'] = server.db.get_ofertas_por_titulo(titulo, limite, offset)
    if len(msg['ofertas']) > 0:
        status = 200

        # Cálculo de offset para paginação de itens
        if offset - limite > 0:
            paginas['anterior'] = url_for('.busca_titulo', titulo=titulo, limite=limite, offset=offset-limite, _external=True)
        ofertas = server.db.get_num_ofertas()
        if offset + limite > ofertas:
            limite = ofertas - (offset + limite)
        if limite:
            paginas['proximo'] = url_for('.busca_titulo', titulo=titulo, limite=limite, offset=offset+limite, _external=True)

        # Conversão de atributos com tipos específicos do MongoDB para string, para que possam ser serializados
        for produto in msg['ofertas']:
            produto['info'] = url_for('.oferta', _id=str(produto['_id']), _external=True)
            produto.pop('_id')
            produto['preco'] = str(produto['preco'])
    return jsonify(paginas=paginas, msg=msg), status, HEADERS


@server.route('/ofertas/preco/<pmin>-<pmax>', methods=['GET'])
def busca_preco(pmin, pmax):
    """
    Rota para busca de ofertas por faixa de preço, no formato <preço mínimo>-<preço máximo>
    """
    limite = request.args.get('limite') or 30
    offset = request.args.get('offset') or 0

    if isinstance(limite, str):
        limite = int(limite)
    if isinstance(offset, str):
        offset = int(offset)

    msg = {'ofertas': 'Não houveram resultados!'}
    paginas = {'anterior': None, 'proximo': None}
    status = 204
    
    msg['ofertas'] = server.db.get_ofertas_por_faixa_de_preco(pmin, pmax, limite, offset)
    if len(msg['ofertas']) > 0:
        status = 200

        # Calculo de offset para paginação de itens
        if offset - limite > 0:
            paginas['anterior'] = url_for('.busca_preco', pmin=pmin, pmax=pmax, limite=limite, offset=offset-limite, _external=True)
        ofertas = server.db.get_num_ofertas()
        if offset + limite > ofertas:
            limite = ofertas - (offset + limite)
        if limite:
            paginas['proximo'] = url_for('.busca_preco', pmin=pmin, pmax=pmax, limite=limite, offset=offset+limite, _external=True)

        # Conversão de atributos com tipos específicos do MongoDB para string, para que possam ser serializados       
        for produto in msg['ofertas']:
            produto['info'] = url_for('.oferta', _id=str(produto['_id']), _external=True)
            produto.pop('_id')
            produto['preco'] = str(produto['preco'])       
    return jsonify(paginas=paginas, msg=msg), status, HEADERS
   
