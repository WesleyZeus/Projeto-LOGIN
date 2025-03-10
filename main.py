from flask import Flask, render_template , request , redirect, url_for
from db import db
from models import Usuario
from flask_login import LoginManager ,login_user ,login_required, logout_user, current_user
import hashlib




app = Flask(__name__)

app.secret_key = "chaveSecreta"

lm = LoginManager(app)
lm.login_view = "login"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)

def hash(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()

@lm.user_loader
def user_loader(id):
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    return usuario


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/registrar", methods=['GET','POST'])
def registrar():
    if request.method == "GET":
        return render_template ('registrar.html')
    
    elif request.method == "POST":

        nome = request.form["nomeForm"]
        senha = request.form["senhaForm"]
        
        novo_usuario = Usuario(nome=nome, senha=hash(senha))
        usuario_existente = Usuario.query.filter_by(nome=nome).first()

        if usuario_existente:
            return render_template("registrar.html", erro="O usuário já está cadastrado")
        
        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for('login'))
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == "POST":
        nome = request.form["nomeForm"]
        senha = request.form["senhaForm"]

        user = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()
        if not user:
            return render_template('login.html', erro="Nome ou senha incorreta!")
        
        login_user(user, remember=True)  

        
        return redirect(url_for('home'))
    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False)