import socket
import threading
import main as m


class Peer:
    """
    classe responsável pela comunicação entre os peers.

    cada instância representa um usuário (peer) que pode:
    - escutar por conexões,
    - conectar-se a outro peer,
    - enviar e receber mensagens,
    - e sincronizar ações de desenho através da rede.
    """

    # construtor
    def __init__(self, ip, porta, username):
        """
        construtor da classe Peer.

        Args:
            ip (str): endereço IP do peer local.
            porta (int): porta TCP usada para escutar conexões.
            username (str): nome de usuário associado a este peer.
        """
        # parâmetros do peer
        self.ip = ip
        self.porta = porta
        self.username = username

        # cria o socket servidor do peer com ipv4 e tcp
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # configura o server socket para sempre utilizar o mesmo ip e porta
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.porta))

        # número máximo de peers conectados (é apenas permitido duas pessoas se conectarem)
        self.max_peers = 1

        # lista para armazenar o peer que estamos conectados
        self.peers = []

        # drawingTools inicial
        self.drawingTools = None

    def escuta(self):
        """
        inicia o modo de escuta do servidor, aguardando novas conexões.

        se o número máximo de conexões for atingido, o peer recusa novas conexões
        enviando uma mensagem de "ocupado". Cada conexão aceita é tratada em uma thread.
        """
        self.server_socket.listen()
        print(f"[{self.username}] Escutando por conexões em {self.ip}:{self.porta}")
        while True:
            try:
                # aceita uma nova conexão
                conn, endereco = self.server_socket.accept()

                # aceita a conexão, manda mensagem que está ocupado e fecha a conexão
                if len(self.peers) >= self.max_peers:
                    print(f"[{self.username}] Conexão recusada de {endereco}: já está conectado a outro peer")
                    msg = self.username + ":msg:Ocupado. Já conectado a outro peer"
                    conn.sendall(msg.encode('utf-8'))
                    conn.close()
                    continue

                print(f"[{self.username}] Conexão aceita de {endereco}")
                self.peers.append(conn)

                # cria uma thread para a função de receber mensagem
                thread = threading.Thread(target=self.recebe_mensagem, args=(conn, endereco))
                thread.daemon = True  # Permite que o programa principal saia mesmo com threads ativas
                thread.start()

            except Exception as e:
                print(f"[{self.username}] Erro ao aceitar conexões: {e}")
                break
        self.server_socket.close()

    def recebe_mensagem(self, peer_socket, endereco):
        """
        recebe mensagens de um peer conectado e as processa conforme o tipo.

        Args:
            peer_socket (socket.socket): socket do peer.
            endereco (tuple): endereço (IP, porta) do peer conectado.

        tipos de mensagens esperadas:
        - "<usuario>:msg:<texto>" → exibe mensagem de chat.
        - "<usuario>:clear" → limpa o canvas.
        - outros → aplicam ações de desenho remoto.
        """
        # buffer para receber a mensagem decodificada e guardar resto de mensagem que podem vir no próximo pacote
        buffer = ""
        while True:
            try:
                # mensagem em binário
                data = peer_socket.recv(4096)
                # se a conexão for fechada pelo outro peer
                if data == b'':
                    peer_socket.close()
                    self.peers.remove(peer_socket)
                    break

                # adiciona os novos dados ao buffer
                buffer += data.decode('utf-8')

                # processa todas as mensagens completas no buffer
                while '\n' in buffer:
                    # separa a primeira mensagem completa ('\n') do resto do buffer
                    messagem, buffer = buffer.split('\n', 1)

                    # ignora mensagens vazias
                    if not messagem:
                        continue

                    # processamento das mensagens
                    parts = messagem.split(":")

                    # se a mensagem tiver mal formada
                    if len(parts) < 2:
                        print(f"[{self.username}] Recebida mensagem corrompida: {messagem}")
                        continue

                    # remove os espaços em branco do início e do final
                    part_1_stripped = parts[1].strip()

                    if part_1_stripped == "msg":
                        # permite ':' na mensagem
                        chat_text = ":".join(parts[2:]).strip()
                        print(f"Mensagem {parts[0] + ':  ' + chat_text}")

                    elif part_1_stripped == "clear":
                        self.drawingTools.clear_canvas()
                        print(f"[{parts[0]}] Apagou o Canvas")

                    elif part_1_stripped == "fechar":
                        print(f"[{parts[0]}] Fechou a conexão")
                        self.peers.remove(peer_socket)
                        break

                    else:
                        # envia uma única e completa mensagem para a aplicar o desenho da rede
                        self.drawingTools.apply_remote_action(messagem)

            except ConnectionResetError:
                break
            except Exception as e:
                print(f"[{self.username}] Erro ao receber mensagem de {endereco}: {e}")
                print(f"Buffer no momento do erro (parcial): {buffer[:200]}")
                peer_socket.close()
                self.peers.remove(peer_socket)
                break

    def conecta(self, peer_ip, peer_porta):
        """
        conecta este peer a outro peer remoto.

        Args:
            peer_ip (str): endereço IP do peer.
            peer_porta (int): porta TCP do peer.

        Returns:
            bool: true se a conexão foi bem-sucedida, false em caso de erro.
        """
        if len(self.peers) >= self.max_peers:
            print(f"[{self.username}] Já esta conectado.")
            return False

        try:
            # cria um novo socket para se conectar a outro peer (age como cliente)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_ip, peer_porta))
            # Adiciona o peer à nossa lista
            self.peers.append(client_socket)
            print(f"[{self.username}] Conectado com sucesso a {peer_ip}:{peer_porta}")

            # inicia uma thread para receber mensagens deste peer ao qual nos conectamos
            thread = threading.Thread(target=self.recebe_mensagem, args=(client_socket, (peer_ip, peer_porta)))
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            print(f"[{self.username}] Não foi possível conectar a {peer_ip}:{peer_porta}. Erro: {e}")
            return False

    def envia_mensagem(self, messagem):
        """
        envia uma mensagem de texto para o peer conectado.
        Args:
            messagem (str): mensagem a ser enviada.
        """
        mensagem_formatada = f"{self.username}:{messagem}\n"
        for peer_socket in self.peers:
            try:
                peer_socket.send(mensagem_formatada.encode('utf-8'))
            except Exception as e:
                print(f"[{self.username}] Falha ao enviar mensagem para um peer: {e}")

    def start(self):
        """
        inicia o peer local.

        permite:
        - conectar a outro peer via comando `connect <ip> <porta>`.
        - enviar mensagens de chat digitando qualquer outro texto.
        """
        listen_thread = threading.Thread(target=self.escuta)
        listen_thread.daemon = True
        listen_thread.start()

        print("Use 'connect <ip> <porta>' para se conectar.")
        print("Qualquer outra coisa que você digitar será enviada como mensagem.")

        while True:
            user_input = input("")
            if user_input.startswith("connect "):
                try:
                    _, ip, porta = user_input.split()
                    self.conecta(ip, int(porta))
                except ValueError:
                    print("Comando inválido. Use: connect <ip> <porta>")
            else:
                self.envia_mensagem("msg:" + user_input)


if __name__ == "__main__":
    """
    Inicio principal do programa.

    descobre o IP local automaticamente, solicita porta e nome do usuário,
    inicia o peer e executa o aplicativo de desenho principal.
    """
    # descobre o IP local automaticamente
    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)

    # espera o usuário digitar uma porta correta
    while True:
        porta = input("Digite a porta em que você quer escutar (ex: 8001): ")
        condicao = porta.isnumeric()
        if condicao:
            porta = int(porta)
            break

    username = input("Digite seu nome de usuário: ")

    peer = Peer(ip_local, porta, username)

    thread = threading.Thread(target=peer.start)
    thread.daemon = True
    thread.start()

    m.main(peer)
