from flask import Flask, request, jsonify
import threading
import os
from relogio import Relogio
import socket
import requests
import time

app = Flask("2")
relogio = Relogio(3, 1)
endereco_ip = socket.gethostbyname(socket.gethostname())

ip_1 = os.getenv('ip1', endereco_ip)
ip_2 = os.getenv('ip2', endereco_ip)
relogios = {'1': f"http://{ip_1}:5656", '2': f"http://{ip_2}:8989"}

lider = None
eleicao_ativa = False
lock = threading.Lock()

url_local=f"http://{endereco_ip}:8989"

def informar_novo_lider(novo_lider):
    global lider
    lider = novo_lider
    for id, url in relogios.items():
        try:
            requests.post(f"{url}/set_lider", json={'lider': novo_lider})
        except Exception as e:
            continue

def verificar_lider():
    global lider
    while True:
        time.sleep(1)
        print(f'lider:{lider}')
        if lider is not None:
            try:
                tempos = {}
                for id, url in relogios.items():
                    response = requests.get(f"{url}/get_tempo")
                    if response.status_code == 200:
                        tempos[int(id)] = response.json().get('tempo')
                
                # Adicionar o tempo do próprio relógio
                tempos[relogio.id] = relogio.get_tempo()

                # Verificar se algum relógio ultrapassou o líder atual
                for id, tempo in tempos.items():
                    if tempo > tempos[lider]:
                        lider = id
                        informar_novo_lider(lider)
                        break

            except Exception as e:
                eleger_e_informar()
        else:
            eleger_e_informar() 

def eleicao():
    global lider
    maior_tempo = relogio.get_tempo()
    novo_lider = relogio.id
    for id, url in relogios.items():
        try:
            response = requests.get(f"{url}/get_tempo")
            tempo = response.json().get('tempo')
            if tempo > maior_tempo:
                maior_tempo = tempo
                novo_lider = int(id)
            elif tempo == maior_tempo and int(id) > novo_lider:
                novo_lider = int(id)
        except Exception as e:
            continue
    lider = novo_lider
    return lider

def eleger_e_informar():
    global lider, eleicao_ativa
    with lock:
        try:
            eleicao_ativa = True
            novo_lider = eleicao()
            lider = novo_lider
            informar_novo_lider(lider)
        finally:
            eleicao_ativa = False

@app.route('/check_eleicao', methods=['GET'])
def check_eleicao():
    global eleicao_ativa
    return jsonify({'eleicao_ativa': eleicao_ativa})

@app.route('/sicronizar', methods=['POST'])
def sicronizar():
    global lider
    try:
        if lider == relogio.id:
            response = requests.get(f"{url_local}/get_tempo")
            tempo_lider = response.json().get('tempo')
        else:
            response = requests.get(f"{relogios[str(lider)]}/get_tempo")
            tempo_lider = response.json().get('tempo')
    except Exception as e:
        return jsonify({'status': f'erro ao obter tempo do líder'})
    
    sincronizacao_resultados = {}
    
    for id, url in relogios.items():
        try:
            if id == lider:
                requests.post(f"{url_local}/set_tempo", json={'tempo': tempo_lider - 1})
                sincronizacao_resultados[relogio.id] = 'sincronizado'
            else:
                requests.post(f"{url}/set_tempo", json={'tempo': tempo_lider - 1})
                sincronizacao_resultados[id] = 'sincronizado'
        except Exception as e:
            sincronizacao_resultados[id] = f'erro ao sincronizar'

    return jsonify({'status': 'sincronizacao concluida', 'resultados': sincronizacao_resultados})

@app.route('/get_tempo', methods=['GET'])
def get_tempo():
    return jsonify({'id': relogio.id, 'tempo': relogio.get_tempo()}), 200

@app.route('/set_tempo', methods=['POST'])
def set_tempo():
    novo_tempo = request.json.get('tempo')
    relogio.set_tempo(novo_tempo)
    return jsonify({'status': 'tempo atualizado'})

@app.route('/set_drift', methods=['POST'])
def set_drift():
    novo_drift = request.json.get('drift')
    relogio.set_drift(novo_drift)
    return jsonify({'status': 'drift atualizado'})

@app.route('/get_drift', methods=['GET'])
def get_drift():
    return jsonify({'id': relogio.id, 'drift': relogio.drift})

@app.route('/set_lider', methods=['POST'])
def set_lider():
    global lider
    lider = request.json.get('lider')
    return jsonify({'status': 'líder atualizado', 'novo_lider': lider})

@app.route('/get_lider', methods=['GET'])
def get_lider():
    global lider
    return jsonify({'lider': lider})

if __name__ == '__main__':
    threading.Thread(target=verificar_lider, daemon=True).start()
    app.run(host=endereco_ip, port=4378)
