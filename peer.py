import socket
import threading

from pyexpat.errors import messages

import main as m

class Peer:

    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username

        # Cria o socket "servidor" do peer para escutar por conexões
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))

        # Lista para armazenar os sockets dos peers aos quais estamos conectados
        self.peers = []

        self.drawingTools = None

    def _listen_for_connections(self):

        while True:
            self.server_socket.listen(1)
            print(f"[{self.username}] Escutando por conexões em {self.host}:{self.port}")
            try:

                # Aceita uma nova conexão
                conn, addr = self.server_socket.accept()
                print(f"[{self.username}] Conexão aceita de {addr}")
                self.server_socket.close()
                # Adiciona o novo peer à nossa lista
                self.peers.append(conn)

                self._handle_peer_messages(conn, addr)


            except Exception as e:
                print(f"[{self.username}] Erro ao aceitar conexões: {e}")
                break

    def _handle_peer_messages(self, peer_socket, addr):
        while True:
            try:
                data = peer_socket.recv(1024)
                if not data:
                    break  # Conexão fechada pelo outro lado
                message = data.decode('utf-8')
                parts = message.split(":")
                if parts[1].strip() == "msg":
                    print(f"[{self.username}] Mensagem {parts[0] + ":  "+ parts[2]}")
                else:
                    self.drawingTools.apply_remote_action(message)
            except ConnectionResetError:
                break  # Conexão forçadamente fechada
            except Exception as e:
                print(f"[{self.username}] Erro ao receber mensagem de {addr}: {e}")
                break

        print(f"[{self.username}] Conexão com {addr} foi perdida.")
        self.peers.remove(peer_socket)
        peer_socket.close()

    def connect_to_peer(self, peer_host, peer_port):
        try:
            # Cria um novo socket para se conectar a outro peer (age como cliente)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_host, peer_port))

            # Adiciona o peer à nossa lista
            self.peers.append(client_socket)
            print(f"[{self.username}] Conectado com sucesso a {peer_host}:{peer_port}")

            # Inicia uma thread para receber mensagens deste peer ao qual nos conectamos
            thread = threading.Thread(target=self._handle_peer_messages, args=(client_socket, (peer_host, peer_port)))
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            print(f"[{self.username}] Não foi possível conectar a {peer_host}:{peer_port}. Erro: {e}")
            return False

    def broadcast(self, message):
        formatted_message = f"{self.username}: {message}"
        for peer_socket in self.peers:
            try:
                peer_socket.sendall(formatted_message.encode('utf-8'))
            except Exception as e:
                print(f"[{self.username}] Falha ao enviar mensagem para um peer: {e}")

    def start(self):
        listen_thread = threading.Thread(target=self._listen_for_connections)
        listen_thread.daemon = True
        listen_thread.start()

        print("Bem-vindo ao chat P2P! Use 'connect <ip> <porta>' para se conectar a um amigo.")
        print("Qualquer outra coisa que você digitar será enviada como mensagem.")

        while True:
            user_input = input("")
            if user_input.startswith("connect "):
                try:
                    _, host, port = user_input.split()
                    self.connect_to_peer(host, int(port))
                except ValueError:
                    print("Comando inválido. Use: connect <ip> <porta>")
            else:
                self.broadcast("msg:" + user_input)

# --- Bloco de Execução ---
if __name__ == "__main__":
    # Descobre o IP local automaticamente
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    # Pede ao usuário uma porta e um nome de usuário

    port = int(input("Digite a porta em que você quer escutar (ex: 8001): "))
    username = input("Digite seu nome de usuário: ")

    peer = Peer(local_ip, port, username)

    thread = threading.Thread(target=peer.start)
    thread.daemon = True
    thread.start()

    m.main(peer)