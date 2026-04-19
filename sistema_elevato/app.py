from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'chave_secreta_elevato'
WEBHOOK_URL_LOGIN = 'http://host.docker.internal:5678/webhook/login'

# ==========================================
# FUNÇÃO AUXILIAR: INICIAR CARRINHO
# ==========================================
def init_carrinho():
    if 'carrinho' not in session:
        session['carrinho'] = {
            'cliente': {},
            'servicos': []
        }

# ==========================================
# ROTAS DE LOGIN
# ==========================================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        payload = {'email': request.form.get('email'), 'senha': request.form.get('senha')}
        try:
            response = requests.post(WEBHOOK_URL_LOGIN, json=payload)
            data = response.json()
            if data.get('status') == 'success':
                session['id_usuario'] = data.get('id_usuario')
                session['nome_usuario'] = data.get('nome')
                init_carrinho()
                return redirect(url_for('pedidos_menu'))
            else:
                flash('Usuário ou senha incorretos.')
        except Exception as e:
            flash(f'Erro de conexão com n8n: {e}')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==========================================
# ROTAS DO PEDIDO (O FLUXO MVC)
# ==========================================

# TELA 1: MENU PRINCIPAL
@app.route('/pedidos')
def pedidos_menu():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    init_carrinho()
    return render_template('pedidos_menu.html', nome_usuario=session['nome_usuario'])

# AÇÃO: NOVO PEDIDO (Limpa o carrinho)
@app.route('/pedidos/novo')
def pedidos_novo():
    session['carrinho'] = {'cliente': {}, 'servicos': []}
    session.modified = True
    return redirect(url_for('pedidos_cliente'))

# TELA 2: INFORMAÇÕES DO CLIENTE
@app.route('/pedidos/cliente', methods=['GET', 'POST'])
def pedidos_cliente():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    init_carrinho()

    # DADOS FALSOS temporários para você ver a tela funcionando (Depois virá do n8n)
    mock_clientes = [{'id': 1, 'nome': 'João Silva'}, {'id': 2, 'nome': 'Empresa XYZ'}]
    mock_vendedores = [{'id': 1, 'nome': 'Otávio Ramaian'}, {'id': 2, 'nome': 'Lorran Kaua'}]

    if request.method == 'POST':
        # Salva tudo no carrinho da sessão
        session['carrinho']['cliente'] = request.form.to_dict()
        session.modified = True
        return redirect(url_for('pedidos_servicos'))

    return render_template('pedidos_cliente.html', 
                           nome_usuario=session['nome_usuario'],
                           carrinho=session['carrinho']['cliente'],
                           clientes=mock_clientes,
                           vendedores=mock_vendedores)

# TELA 3: SERVIÇOS
@app.route('/pedidos/servicos')
def pedidos_servicos():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    init_carrinho()
    
    mock_categorias = [{'id': 1, 'nome': 'Tendas'}, {'id': 2, 'nome': 'Mesas'}]
    mock_tipos = [{'id': 1, 'nome': 'Locação'}, {'id': 2, 'nome': 'Venda'}]

    return render_template('pedidos_servicos.html', 
                           nome_usuario=session['nome_usuario'],
                           carrinho_servicos=session['carrinho']['servicos'],
                           categorias=mock_categorias,
                           tipos_pedido=mock_tipos)

# TELA 4: RESUMO
@app.route('/pedidos/resumo')
def pedidos_resumo():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    init_carrinho()
    
    # Calcula o total geral para mostrar na tela
    total_geral = sum(float(item['vl_total']) for item in session['carrinho']['servicos'])

    return render_template('pedidos_resumo.html', 
                           nome_usuario=session['nome_usuario'],
                           carrinho=session['carrinho'],
                           total_geral=total_geral)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)