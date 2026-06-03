from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  

DATABASE = 'avaliacoes.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto TEXT NOT NULL,
            estrelas INTEGER NOT NULL,
            comentario TEXT NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()


@app.route('/')
def serve_index():
    # os.path.abspath limpa o caminho removendo o '..' e evita o erro 404 no Render
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'front-end'))
    return send_from_directory(frontend_dir, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'front-end'))
    return send_from_directory(frontend_dir, path)

@app.route('/api/avaliacao', methods=['POST'])
def salvar_avaliacao():
    data = request.get_json()
    
    projeto = data.get('projeto')
    estrelas = data.get('estrelas')
    comentario = data.get('comentario')
    
    if not projeto or not estrelas or not comentario:
        return jsonify({'status': 'erro', 'mensagem': 'Dados incompletos!'}), 400
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO feedbacks (projeto, estrelas, comentario) VALUES (?, ?, ?)',
            (projeto, int(estrelas), comentario)
        )
        conn.commit()
        conn.close()
        return jsonify({'status': 'sucesso', 'mensagem': 'Avaliação enviada com sucesso!'}), 201
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': f'Erro interno: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)