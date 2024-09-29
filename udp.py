import socket
import threading
import argparse


def get_local_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception as e:
        print(f"Erro ao tentar obter o IP local: {e}")
        return "127.0.0.1"


def verificar_server_executando(server_ip, porta):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(b'ping', (server_ip, porta))
        sock.settimeout(2)
        dados, endereco = sock.recvfrom(1024)
        if dados:
            print(f"O server já está executando em {server_ip}:{porta}")
            return True
    except Exception as e:
        print("server não encontrado. Erro:", str(e))
        return False
    finally:
        sock.close()


clients = set()


def server(server_ip, porta):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server_ip, porta))

    print(f"server UDP está aguardando mensagens em {server_ip}:{porta}...")

    while True:
        dados, endereco = sock.recvfrom(1024)
        print(f"Mensagem recebida de {endereco}: {dados.decode()}")
        resposta = dados.decode()
        
        if endereco not in clients:
            clients.add(endereco)
        
        for client in clients:
            sock.sendto(resposta.encode(), client)


def receber_mensagens(sock):
    while True:
        try:
            dados, endereco = sock.recvfrom(1024)
            print(f"\nMensagem recebida do server: {dados.decode()} de {endereco}")
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            break


def client(server_ip, porta):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    thread_receber = threading.Thread(target=receber_mensagens, args=(sock,))
    thread_receber.daemon = True
    thread_receber.start()

    while True:
        mensagem = input("Digite a mensagem a ser enviada: ")

        if mensagem.lower() == 'sair':
            print("Saindo do client...")
            break

        sock.sendto(mensagem.encode(), (server_ip, porta))
        print("Mensagem enviada ao server.")


def iniciar_server_com_verificacao(server_ip, porta):
    if not verificar_server_executando(server_ip, porta):
        thread_server = threading.Thread(target=server, args=(server_ip, porta))
        thread_server.daemon = True
        thread_server.start()
        print("server iniciado.")
    else:
        print("O server já está em execução, não será iniciado novamente.")


def main(args):
    server_ip = args.ip if args.ip else get_local_ip()
    porta = args.porta

    iniciar_server_com_verificacao(server_ip, porta)

    thread_client = threading.Thread(target=client, args=(server_ip, porta))
    thread_client.daemon = True
    thread_client.start()
    thread_client.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="server e client UDP")
    parser.add_argument('--ip', type=str, help='IP do server')
    parser.add_argument('--porta', type=int, default=5005, help='Porta do server')

    args = parser.parse_args()

    main(args)

# client não é server, o server deve mandar a mensagem pro client após recebe-la