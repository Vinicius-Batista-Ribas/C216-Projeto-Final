from flask import Flask, render_template, request, redirect, url_for, jsonify
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

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')

@app.route('/download/<int:mod_id>', methods=['GET'])
def baixar_mod(mod_id):

    response = requests.get(f"{API_BASE_URL}/api/v1/home/mod/{mod_id}")

    if response.status_code == 200:
        mod = response.json()  # Converte a resposta em um dicionário Python
        # Agora você pode acessar os dados do mod diretamente
        nome_mod = mod.get('nome')
        nome_jogo = mod.get('jogo')
        descricao = mod.get('descricao')
        versao = mod.get('versao')
        autores = mod.get('autores')
        categoria = mod.get('categoria')
        tamanho = mod.get('tamanho')

        # Exemplo de como você pode processar esses dados
        conteudo_arquivo = f"Parabéns! Você baixou seu mod de {nome_jogo}!\n"
        conteudo_arquivo += f"Nome do Mod: {nome_mod}\n"
        conteudo_arquivo += f"Descrição: {descricao}\n"
        conteudo_arquivo += f"Versão: {versao}\n"
        conteudo_arquivo += f"Autores: {autores}\n"
        conteudo_arquivo += f"Categoria: {categoria}\n"
        conteudo_arquivo += f"Tamanho: {tamanho}\n"
        
        # Aqui você pode salvar o conteúdo do arquivo, exibir no console, etc.
        print(conteudo_arquivo)
    else:
        print("Erro ao buscar os dados do mod.")
    caminho_arquivo = f"downloads/{nome_mod}_baixado.txt"
    os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)

    with open(caminho_arquivo, 'w') as file:
        file.write(conteudo_arquivo)
        
    return os.sendfile(caminho_arquivo, as_attachment=True, download_name=f"{nome_mod}_mod.txt")
        