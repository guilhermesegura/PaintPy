# cliente_oo.py

import socket

class Cliente:

    def __init__(self, host='127.0.0.1', port=65432):

        self.host = host
        self.port = port
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _comunicar(self):
        try:
            while True:
                mensagem = input("Digite sua mensagem (ou 'sair' para terminar): ")
                if mensagem.lower() == 'sair':
                    break

                # Envia a mensagem codificada em bytes
                self.socket_cliente.sendall(mensagem.encode('utf-8'))

                # Recebe a resposta do servidor
                data = self.socket_cliente.recv(1024)
                print(f"Servidor (eco): {data.decode('utf-8')}")

        except ConnectionResetError:
            print("A conexão foi perdida com o servidor.")
        finally:
            print("Desconectando do servidor.")

    def start(self):

        try:
            self.socket_cliente.connect((self.host, self.port))
            print(f"Conectado com sucesso ao servidor em {self.host}:{self.port}")
            self._comunicar()
        except ConnectionRefusedError:
            print("[ERRO] Não foi possível conectar ao servidor. Ele está online?")
        finally:
            self.socket_cliente.close()


# --- Bloco de Execução ---
if __name__ == "__main__":
    cliente = Cliente()
    cliente.start()