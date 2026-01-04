from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
import requests
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_organized.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Compromisso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False)
    horario = db.Column(db.String(10), nullable=False)
    tipo = db.Column(db.String(50))
    concluido = db.Column(db.Boolean, default=False)
    
with app.app_context():
    db.create_all()
    
Telegram_Token = "8558280767:AAG4m_aU8j4ctJjLW9PXVXPuHgtqfzyvGPU"
Chat_ID = "1993816277"

def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{Telegram_Token}/sendMessage"
        data = {"chat_id": Chat_ID, "text": mensagem}
        requests.post(url, data=data)
        print("Mensagem enviada ao Telegram")
    except Exception as e:
        print(f"Erro ao enviar ao Telegram: {e}")
        
def vigilante():
    print("🔦 Vigiando... (MODO DEBUG ATIVADO)")
    
    # Dicionário atual (Se o banco tiver "Sexta", isso aqui vai dar erro de busca)
    dias_translate = {
            0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira",
            4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
        }
    
    while True:
        try:
            horario_agora = datetime.now().strftime("%H:%M")
            hoje_numero = datetime.now().weekday()
            dia_calculado = dias_translate[hoje_numero]
            
            # Print para saber o que o robô está pensando
            print(f"\n--- ROBÔ: Buscando por '{dia_calculado}' às '{horario_agora}' ---")

            with app.app_context():
                # 1. Vamos ver o que tem no banco de dados DE VERDADE
                todos_compromissos = Compromisso.query.all()
                print(f"DEBUG: Existem {len(todos_compromissos)} tarefas totais no banco.")
                for c in todos_compromissos:
                    print(f"   -> Banco tem: '{c.titulo}' marcado para '{c.dia_semana}' às '{c.horario}'")

                # 2. A busca oficial
                compromissos = Compromisso.query.filter_by(
                    dia_semana=dia_calculado,
                    horario=horario_agora,
                    concluido=False
                ).all()
                
                print(f"DEBUG: Tarefas encontradas para AGORA: {len(compromissos)}")
                
                for item in compromissos:
                    titulo = item.titulo
                    tipo = item.tipo
                    
                    print(f"ACHEI! Enviando mensagem para {titulo}...")
                    msg_macro = f"ALERTA URGENTE: Hora de {titulo} ({tipo})!!"
                    enviar_telegram(msg_macro)
                    
                    time.sleep(60)
            
            # Espera 30 segundos
            time.sleep(30)
            
        except Exception as e:
            print(f"Erro grave no vigilante: {e}")
            time.sleep(30)
            
@app.route('/')
def index():
    compromissos = Compromisso.query.order_by(Compromisso.horario).all()
    return render_template('index.html', compromissos=compromissos)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    titulo = request.form.get('titulo')
    dia = request.form.get('dia')
    horario = request.form.get('horario')
    tipo = request.form.get('tipo')
    
    novo_compromisso = Compromisso(titulo=titulo, dia_semana=dia, horario=horario, tipo=tipo)
    db.session.add(novo_compromisso)
    db.session.commit()
    
    msg_info = f"📅 Lembrete: Você tem um '{titulo}' agendado para instantes!!"
    enviar_telegram(msg_info)
    
    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    tarefa = Compromisso.query.get_or_404(id)
    db.session.delete(tarefa)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    thread_vigilante = threading.Thread(target=vigilante)
    thread_vigilante.daemon = True
    thread_vigilante.start()
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
                

"""from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
import requests
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_organized.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Compromisso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False)
    horario = db.Column(db.String(10), nullable=False)
    tipo = db.Column(db.String(50))
    concluido = db.Column(db.Boolean, default=False)
    
with app.app_context():
    db.create_all()
    
Telegram_Token = "8558280767:AAG4m_aU8j4ctJjLW9PXVXPuHgtqfzyvGPU"
Chat_ID = "1993816277"

def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{Telegram_Token}/sendMessage"
        data = {"chat_id": Chat_ID, "text": mensagem}
        requests.post(url, data=data)
        print("Mensagem enviada ao Telegram")
    except Exception as e:
        print(f"Erro ao enviar ao Telegram: {e}")
        
def vigilante():
    print("🔦 Vigiando...")
    
    dias_translate = {
            0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira",
            4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
        }
    
    while True:
        try: 
            horario_agora = datetime.now().strftime("%H:%M")
            dia_atual_num = datetime.now().weekday()
            dia_atual_texto = dias_translate[dia_atual_num]
            
            with app.app_context():
                compromissos = Compromisso.query.filter_by(
                    dia_semana=dia_atual_texto,
                    horario=horario_agora
                ).all()
                
                for item in compromissos:
                    titulo = item.titulo
                    tipo = item.tipo
                    
                    msg = f"⏰ ALERTA URGENTE: Hora de {titulo} ({tipo})!!"
                    enviar_telegram(msg)
                    time.sleep(60)
            
            time.sleep(30)
        
        except Exception as e:
            print(f"❌ Deu errado com o vigilante: {e}")
            time.sleep(30)
        
@app.route('/')
def index():
    compromissos = Compromisso.query.order_by(Compromisso.horario).all()
    return render_template('index.html', compromissos=compromissos)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    titulo = request.form.get('titulo')
    dia = request.form.get('dia')
    horario = request.form.get('horario')
    tipo = request.form.get('tipo')
    
    novo_compromisso = Compromisso(titulo=titulo, dia_semana=dia, horario=horario, tipo=tipo)
    db.session.add(novo_compromisso)
    db.session.commit()
    
    enviar_telegram(f"Compromisso novo: {titulo} às {horario}")
    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    tarefa = Compromisso.query.get_or_404(id)
    db.session.delete(tarefa)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    thread_do_vigia = threading.Thread(target=vigilante)
    thread_do_vigia.daemon = True
    thread_do_vigia.start()
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)"""