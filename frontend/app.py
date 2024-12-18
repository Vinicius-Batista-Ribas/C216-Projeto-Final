from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import requests
import os

app = Flask(__name__)

# Definindo as variáveis de ambiente
API_BASE_URL = "http://backend:8000"

# Rota para a página inicial
@app.route('/')
def home():
    return render_template('index.html')

# Rota para listar todos os mods
@app.route('/mods', methods=['GET'])
def listar_mods():
    response = requests.get(f'{API_BASE_URL}/api/v1/home/')
    try:
        mods = response.json()
    except:
        mods = []
    return render_template('mods.html', mods=mods)

# Rota para exibir o formulário de cadastro de mod
@app.route('/cadastro', methods=['GET'])
def inserir_mod_form():
    return render_template('cadastro.html')

# Rota para enviar os dados do formulário de cadastro de mod para a API
@app.route('/inserir', methods=['POST'])
def inserir_mod():

    nome = request.form['nome']
    jogo = request.form['jogo']
    descricao = request.form['descricao']
    versao = request.form['versao']
    autores = request.form['autores']
    categoria = request.form['categoria']
    tamanho = request.form['tamanho']

    payload = {
        'nome': nome,
        'jogo': jogo,
        'descricao': descricao,
        'versao': versao,
        'autores': autores,
        'categoria': categoria,
        'tamanho': tamanho
    }

    response = requests.post(f'{API_BASE_URL}/api/v1/home/', json=payload)
    
    if response.status_code == 201:
        return redirect(url_for('listar_mods'))
    else:
        return "Erro ao inserir mod", 500

# Rota para exibir o formulário de edição de mod
@app.route('/atualizar/<int:mod_id>', methods=['GET'])
def atualizar_mod_form(mod_id):

    response = requests.get(f"{API_BASE_URL}/api/v1/home/mod/{mod_id}")
    
    if response.status_code == 200:
        mod = response.json()
        return render_template('atualizar.html', mod=mod)
    else:
        return "Mod não encontrado", 404

# Rota para enviar os dados do formulário de edição de mod para a API
@app.route('/atualizar/mod/<int:mod_id>', methods=['POST'])
def atualizar_mod(mod_id):

    nome = request.form.get('nome')
    jogo = request.form.get('jogo')
    descricao = request.form.get('descricao')
    versao = request.form.get('versao')
    autores = request.form.get('autores')
    categoria = request.form.get('categoria')
    tamanho = request.form.get('tamanho')

    
    payload = {
        'nome': nome,
        'jogo': jogo,
        'descricao': descricao,
        'versao': versao,
        'autores': autores,
        'categoria': categoria,
        'tamanho': tamanho
    }
    
    response = requests.patch(f"{API_BASE_URL}/api/v1/home/mod/{mod_id}", json=payload)

    if response.status_code == 200:
        return redirect(url_for('listar_mods'))
    else:
        return "Erro ao atualizar mod", 500

# Rota para excluir um mod
@app.route('/excluir/<int:mod_id>', methods=['POST'])
def excluir_mod(mod_id):
    response = requests.delete(f"{API_BASE_URL}/api/v1/home/mod/{mod_id}")
    
    if response.status_code == 200:
        return redirect(url_for('listar_mods'))
    else:
        return "Erro ao excluir mod", 500

# Rota para resetar o database
@app.route('/reset-database', methods=['GET'])
def resetar_database():
    response = requests.delete(f"{API_BASE_URL}/api/v1/home/reset/")
    
    if response.status_code == 200:
        return render_template('confirmacao.html')
    else:
        return "Erro ao resetar o database", 500


@app.route('/download/<int:mod_id>', methods=['GET'])
def baixar(mod_id):

    response = requests.get(f"{API_BASE_URL}/api/v1/home/mod/{mod_id}")
    
    if response.status_code == 200:
        mod = response.json()
        
        # Criar o conteúdo do arquivo de texto
        file_content = (
            f"Parabéns, você baixou o mod do jogo {mod['jogo']}!\n"
            f"Nome do mod: {mod['nome']}\n"
            f"Versão: {mod['versao']}\n"
            f"Autores: {mod['autores']}\n"
            f"Descrição: {mod['descricao']}"
        )
        
        # Criar um arquivo em memória
        file = BytesIO(file_content.encode('utf-8'))
        file.seek(0)  # Reposicionar o ponteiro para o início do arquivo

        # Retornar o arquivo para download
        return send_file(
            file,
            as_attachment=True,
            download_name=f"mod_{mod_id}_download.txt",
            mimetype='text/plain'
        )
    
    else:
        # Retornar erro caso o mod não seja encontrado
        return jsonify({"error": "Mod não encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')



