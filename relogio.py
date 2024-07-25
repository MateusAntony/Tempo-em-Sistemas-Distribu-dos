import threading
import time

class Relogio():
    def __init__(self, id, drift):
        self.id=id
        self.drift=drift
        self.tempo=0
        self.ligado= True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.incremento)  # Cria uma thread para incrementar o tempo
        self.thread.start()  # Inicia a thread

    def incremento(self):
        # Incrementa o tempo do relógio em intervalos definidos pelo drift
        while self.ligado:
                print(self.tempo)
                time.sleep(self.drift)
                self.tempo += 1

    def get_tempo(self):
        with self.lock:
            return self.tempo
    
    def set_tempo(self,novo_tempo):
        with self.lock:
            self.tempo = novo_tempo
            return self.tempo
        
    def set_drift(self,novo_drift):
        with self.lock:
            self.drift= novo_drift
            return self.drift 