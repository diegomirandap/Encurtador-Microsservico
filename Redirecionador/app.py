import os
from flask import Flask, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    hits = db.Column(db.Integer, default=0)

@app.route('/<short_code>', methods=['GET'])
def redirecionar(short_code):
    url_entry = URL.query.filter_by(short_code=short_code).first_or_404()
    
    # Incrementa o hit (Ainda estamos no modelo de banco compartilhado)
    url_entry.hits += 1
    db.session.commit()
    
    return redirect(url_entry.original_url)

@app.route('/stats/<short_code>', methods=['GET'])
def stats(short_code):
    url_entry = URL.query.filter_by(short_code=short_code).first_or_404()
    return jsonify({"hits": url_entry.hits})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) # Porta 5000