'''
http://localhost:5000/apidocs
acessa o swagger e a doc/operaçao da api


http://localhost:5000/api/v1/short-urls
body: {
    "url": "https://www.google.com",
    "owner-id": "dogo"
}
retorna a url


http://localhost:5000/api/v1/short-urls/qt1Xov
mostra os dados da url encurtada


http://localhost:5001/qt1Xov
redireciona


'''

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
    
    # Note que agora apontamos para a porta do serviço de leitura (5000)
    return jsonify({"short_code": f"http://localhost:5000/{codigo}"}), 201

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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000) # Porta 5000