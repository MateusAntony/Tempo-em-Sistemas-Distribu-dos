import requests
import socket
import os

endereco_ip = socket.gethostbyname(socket.gethostname())
port = int(os.getenv('port', 5656))
base_url = f"http://{endereco_ip}:{port}"
ip =  os.getenv('ip', endereco_ip)
print(base_url)

def menu():
    print("\nMenu:")
    print("1 - Mudar drift")
    print("2 - Sincronizar com o líder")
    print("3 - Ver o drift")
    print("4 - Ver quem é o líder")
    print("5 - Sair")
    print("6 - Mostrar o tempo atual ")

def mudar_drift():
    novo_drift = int(input("Digite o novo drift: "))
    response = requests.post(f"{base_url}/set_drift", json={'drift': novo_drift})
    if response.status_code == 200:
        print("Drift atualizado com sucesso.")
    else:
        print("Erro ao atualizar drift.")

def sicronizar_com_lider():
    response = requests.post(f"{base_url}/sicronizar")
    if response.status_code == 200:
        print("Sincronização concluída:", response.json())
    else:
        print("Erro ao sincronizar com o líder.")

def ver_drift():
    response = requests.get(f"{base_url}/get_drift")
    if response.status_code == 200:
        data = response.json()
        print(f"Drift atual: {data.get('drift')}")
    else:
        print("Erro ao obter o drift.")

def ver_lider():
    response = requests.get(f"{base_url}/get_lider")
    if response.status_code == 200:
        data = response.json()
        print(f"Líder atual: {data.get('lider')}")
    else:
        print("Erro ao obter o líder.")

def ver_tempo():
    response = requests.get(f"{base_url}/get_tempo")
    if response.status_code == 200:
        data = response.json()
        print(f"tempo atual: {data.get('tempo')}")
    else:
        print("Erro ao obter o tempo.")

def main():
    while True:
        menu()
        choice = input("Escolha uma opção: ")
        if choice == "1":
            mudar_drift()
        elif choice == "2":
            sicronizar_com_lider()
        elif choice == "3":
            ver_drift()
        elif choice == "4":
            ver_lider()
        elif choice == "5":
            break
        elif choice == "6":
            ver_tempo()
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
