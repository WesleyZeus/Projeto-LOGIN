import pytest
from flask import Flask
from main import *  # Importe a aplicação e o banco de dados
from flask_login import *

# Fixture para configurar o banco de dados para os testes
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # Banco de dados em memória
    app.config['SECRET_KEY'] = "chaveSecreta"
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Cria as tabelas temporárias para os testes
        yield client
        # Remove a sessão após o teste
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Drope as tabelas após os testes



# Teste para registrar um novo usuário
def test_registrar(client):
    response = client.post('/registrar', data=dict(
        nomeForm='novo_usuario',
        senhaForm='senhaSegura123'
    ), follow_redirects=True)
    
    # Verifica se o redirecionamento para o login aconteceu após o cadastro
    assert response.status_code == 200
    assert 'O usuário já está cadastrado' not in response.data.decode('utf-8') # Confirma que não apareceu erro

    # Verifica se o usuário foi realmente inserido no banco
    user = Usuario.query.filter_by(nome='novo_usuario').first()
    assert user is not None
    assert user.nome == 'novo_usuario'



# Teste para tentar registrar um usuário já existente
def test_registrar_usuario_existente(client):
    # Primeiro, registramos um usuário
    client.post('/registrar', data=dict(
        nomeForm='usuario_existente',
        senhaForm='senhaSegura123'
    ), follow_redirects=True)
    
    # Tentamos registrar o mesmo usuário novamente
    response = client.post('/registrar', data=dict(
        nomeForm='usuario_existente',
        senhaForm='senhaSegura123'
    ), follow_redirects=True)
    
    # Verifica se a mensagem de erro foi retornada
    assert "O usuário já está cadastrado" in response.data.decode('utf-8')


# Teste para o login com dados corretos
def test_login_valid(client):
    # Primeiro, criamos um novo usuário
    client.post('/registrar', data=dict(
        nomeForm='usuario_teste',
        senhaForm='senhaSegura123'
    ), follow_redirects=True)

    # Agora, fazemos o login com esse usuário
    response = client.post('/login', data=dict(
        nomeForm='usuario_teste',
        senhaForm='senhaSegura123'
    ), follow_redirects=True)
    
    # Verifica se a resposta do login é o redirecionamento para a home
    assert response.status_code == 200
    assert "home" in response.data.decode('utf-8')

# Teste para o login com dados incorretos
def test_login_invalid(client):
    # Primeiro, criamos um novo usuário
    client.post('/registrar', data=dict(
        nomeForm='usuario_teste',
        senhaForm='senhaSegura123'
    ), follow_redirects=True)

    # Agora, tentamos fazer o login com uma senha errada
    response = client.post('/login', data=dict(
        nomeForm='usuario_teste',
        senhaForm='senhaErrada'
    ), follow_redirects=True)
    
    # Verifica se a mensagem de erro de login incorreto foi retornada
    assert "Nome ou senha incorreta!" in response.data.decode('utf-8')
    

# Teste para o logout
def test_logout(client):
    # Primeiro, registramos e logamos um usuário
    client.post('/registrar', data=dict(
        nomeForm='usuario_logout',
        senhaForm='senhaSegura123'
    ), follow_redirects=True)
    
    response = client.post('/login', data=dict(
        nomeForm='usuario_logout',
        senhaForm='senhaSegura123'
    ), follow_redirects=True)
    
    # Verifica se a resposta do login foi bem-sucedida
    assert response.status_code == 200
    assert b'home' in response.data

    
    # Agora, fazemos o logout
    response = client.get('/logout', follow_redirects=True)
    
    # Verifica se após o logout, o usuário foi redirecionado para a home
    assert b'home' in response.data
