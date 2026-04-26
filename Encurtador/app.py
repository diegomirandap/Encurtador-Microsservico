import os
import string
import random
from flasgger import Swagger
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
swagger = Swagger(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    owner_id = db.Column(db.String(30), unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    hits = db.Column(db.Integer, default=0)

def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/api/v1/short-urls', methods=['POST'])
def encurtar():
    """
    Cria um novo link encurtado
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            url:
              type: string
              example: "https://google.com"
            owner-id:
              type: string
              example: "roger"
    responses:
      201:
        description: Link criado com sucesso
    """
    data = request.json
    url_original = data.get('url')
    owner_id = data.get('owner-id')
    
    codigo = generate_short_code()
    nova_url = URL(original_url=url_original, short_code=codigo, owner_id=owner_id)
    
    db.session.add(nova_url)
    db.session.commit()
    
    # Note que agora apontamos para a porta do serviço de leitura (5001)
    return jsonify({"short_code": f"http://localhost:5001/{codigo}"}), 201

@app.route('/api/v1/short-urls/<short_code>', methods=['GET'])
def getShortUrl(short_code):
    """
    Obtém os dados de um link encurtado através do seu código
    ---
    parameters:
      - name: short_code
        in: path
        type: string
        required: true
        description: O código curto da URL (ex AbCdEf)
    responses:
      200:
        description: Detalhes encontrados
      404:
        description: URL não encontrada
    """
    url_data = URL.query.filter_by(short_code=short_code).first()
    
    if not url_data:
        return jsonify({"error": "URL não encontrada"}), 404
    
    return jsonify({
        "original_url": url_data.original_url,
        "short_code": url_data.short_code,
        "owner_id": url_data.owner_id,
        "created_at": url_data.created_at,
        "hits": url_data.hits
    }), 200

@app.route('/api/v1/short-urls/delete/<short_code>', methods=['DELETE'])
def deleteShortUrl(short_code):
    """
    Exclui os dados de um link encurtado através do seu código
    ---
    parameters:
      - name: short_code
        in: path
        type: string
        required: true
        description: O código curto da URL (ex AbCdEf)
      - name: owner_id
        in: query
        type: string
        required: false
        description: ID do proprietário (obrigatório para DELETE)
    responses:
      200:
        description: URL deletada
      404:
        description: URL não encontrada
      400:
        description: owner_id obrigatório para DELETE
    """
    owner_id = request.args.get('owner_id')
    if not owner_id:
        return jsonify({"error": "owner_id required"}), 400
    url = URL.query.filter_by(short_code=short_code, owner_id=owner_id).first()
    if not url:
        return jsonify({"error": "URL not found or not owned by user"}), 404
    db.session.delete(url)
    db.session.commit()
    return '', 200


@app.route('/api/v1/admin/short-url', methods=['GET'])
def getAllShortUrl():
    """
    Retorna todas as URLs com paginação (endpoint admin)
    ---
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Página a ser retornada
      - name: per_page
        in: query
        type: integer
        default: 10
        description: Número de itens por página
    responses:
      200:
        description: Lista de URLs
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    urls = URL.query.paginate(page=page, per_page=per_page, error_out=False)
    result = []
    for url in urls.items:
        result.append({
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "owner_id": url.owner_id,
            "created_at": url.created_at,
            "hits": url.hits
        })
    return jsonify({
        "urls": result,
        "total": urls.total,
        "pages": urls.pages,
        "current_page": page
    }), 200


@app.route('/api/v1/<owner_id>/urls', methods=['GET'])
def getUserUrls(owner_id):
    """
    Retorna as URLs do usuário com paginação
    ---
    parameters:
      - name: owner_id
        in: path
        type: string
        required: true
        description: ID do proprietário
      - name: page
        in: query
        type: integer
        default: 1
        description: Página a ser retornada
      - name: per_page
        in: query
        type: integer
        default: 10
        description: Número de itens por página
    responses:
      200:
        description: Lista de URLs do usuário
      400:
        description: owner_id obrigatório
    """
    if not owner_id:
        return jsonify({"error": "owner_id required"}), 400
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    urls = URL.query.filter_by(owner_id=owner_id).paginate(page=page, per_page=per_page, error_out=False)
    result = []
    for url in urls.items:
        result.append({
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "owner_id": url.owner_id,
            "created_at": url.created_at,
            "hits": url.hits
        })
    return jsonify({
        "urls": result,
        "total": urls.total,
        "pages": urls.pages,
        "current_page": page
    }), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000) # Porta 5000