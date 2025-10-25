import tkinter as tk

"""
Essa classe foi criada com auxilio de IA 
e das documentações do TKinter 
conforme está na sessão 7 da documentação
"""

class DrawingTools:
    """
    classe responsável pelas ferramentas de desenho.
    Controla as ações do usuário no canvas, como desenhar, apagar e inserir texto,
    além de sincronizar essas ações com outro peer conectados.
    """
    def __init__(self, canvas, peer):
        """
        inicializa as variáveis e configurações padrão das ferramentas de desenho.

        Args:
            canvas (tk.Canvas): área de desenho principal.
            peer (Peer): objeto responsável pela comunicação em rede.
        """
        self.canvas = canvas
        self.pen_color = "#000000"
        self.pen_size = 2 # Also used for text size
        self.tool = "pen"
        self.id_last_shape = None
        self.start_x, self.start_y = None, None

        # --- For text tool ---
        self.text_entry_widget = None
        self.text_entry_canvas_id = None
        self.text_font = "Arial" # Default font
        self.text_color = "#000000" # Default text color

        self.peer = peer

    def set_color(self, color):
        """
        define a cor do pincel e do texto.

        Args:
            color (str): nova cor em formato hexadecimal (ex: "#FF0000").
        """
        self.pen_color = color
        self.text_color = color

    def set_size(self, size):
        """
        define o tamanho do pincel e do texto.

        Args:
            size (int | str): novo tamanho.
        """
        self.pen_size = int(size)

    def set_tool(self, tool_name):
        """
        define a ferramenta ativa (pincel, borracha, linha, retângulo, círculo ou texto).
        Usado ao inicializar o programa

        Args:
            tool_name (str): nome da ferramenta.
        """
        self._cleanup_temp_tools()

        self.tool = tool_name
        self.canvas.config(cursor="crosshair" if tool_name in ["pen", "eraser", "line", "rectangle", "circle", "text"] else "arrow")
        self.start_x, self.start_y = None, None

    def _cleanup_temp_tools(self):
        """
        Remove o text widget inicial.
        """
        if self.text_entry_widget:
            self.text_entry_widget.destroy()
            self.text_entry_widget = None
        if self.text_entry_canvas_id:
            self.canvas.delete(self.text_entry_canvas_id)
            self.text_entry_canvas_id = None


    def start_action(self, event):
        """
        inicia uma ação de desenho de acordo com a ferramenta selecionada.
        Função executada ao pressionar o botão esquerdo do mouse

        Args:
            event (tk.Event): evento de clique no canvas.
        """
        self.start_x, self.start_y = event.x, event.y

        if self.tool in ["pen", "eraser"]:
            string_data = self.draw_line(self.start_x, self.start_y)
            msg = ":".join(string_data)
            if self.peer:
                self.peer.envia_mensagem(msg)

        if self.tool in ["line", "rectangle", "circle"]:
            pass


        elif self.tool == "text":
            self._cleanup_temp_tools()

            self.text_entry_widget = tk.Entry(self.canvas, bg="lightgrey", fg=self.text_color,
                                              font=(self.text_font, self.pen_size))
            self.text_entry_canvas_id = self.canvas.create_window(event.x, event.y,
                                                                  window=self.text_entry_widget,
                                                                  anchor=tk.NW, tags="temp_text_entry")
            self.text_entry_widget.focus_set()
            # Bind Return key to finalize text
            self.text_entry_widget.bind("<Return>", self._finalize_text)
            # Bind Escape key to cancel text entry
            self.text_entry_widget.bind("<Escape>", self._cancel_text_entry)


    def apply_remote_action(self, message):
        """
        aplica no canvas uma ação recebida de outro peer.

        essa função interpreta a mensagem recebida de outro usuário e reproduz
        a ação correspondente no canvas local. Suporta todas as ferramentas
        disponíveis: linha, retângulo, círculo, pincel, borracha e texto.

        a mensagem deve estar no formato separado por ':':

            <username>:<tool>:<color>:<size>:<x1>:<y1>:<x2>:<y2>:<extra_data>

        onde:
            - username: nome do usuário que enviou a ação
            - tool: ferramenta usada ('line', 'rectangle', 'circle', 'pen', 'eraser', 'text')
            - color: cor do desenho/texto
            - size: tamanho do pincel ou fonte
            - x1, y1: coordenadas iniciais
            - x2, y2: coordenadas finais (não usado para texto)
            - extra_data: texto digitado (apenas para ferramenta 'text')

        o método realiza os seguintes passos:
            1. Divide a mensagem em partes usando ':'.
            2. Converte os valores necessários para inteiro (coordenadas e tamanho).
            3. Verifica qual ferramenta foi usada.
            4. Desenha a forma correspondente no canvas:
                - line: linha reta
                - rectangle: retângulo
                - circle: círculo (oval)
                - pen: pincel
                - eraser: borracha (linha branca)
                - text: insere texto no canvas
            5. Em caso de erro, exibe mensagem no console sem travar o programa.

        Args:
            message (str): mensagem recebida contendo os dados da ação.
        """
        try:
            parts = message.split(':')
            tool = parts[1].strip()
            color = parts[2]
            x1 = int(parts[4])
            y1 = int(parts[5])
            size = int(parts[3])
            if tool != "text":
                x2 = int(parts[6])
                y2 = int(parts[7])
            else:
                extra_data = parts[6]

            if tool == "line":

                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=size,
                                            capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")

            elif tool == "rectangle":

                bbox = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
                self.canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3],
                                             outline=color, width=size, tags="drawn_item")

            elif tool == "circle":

                bbox = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
                self.canvas.create_oval(bbox, outline=color, width=size, tags="drawn_item")

            elif tool == "pen":
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=size,
                                        capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")

            elif tool == "eraser":

                self.canvas.create_line(x1, y1, x2, y2, fill="white", width=size * 2,
                                       capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")

            elif tool == "text":
                text_content = extra_data
                if text_content:
                    font_size = max(1, size)
                    self.canvas.create_text(x1, y1, text=text_content, anchor=tk.NW,
                                            font=(self.text_font, font_size),  fill=color, tags="drawn_item")

        except Exception as e:
            print(f"Erro ao aplicar ação remota: {e}. Mensagem: '{message}'")


    def perform_action(self, event):
        x, y = event.x, event.y
        """
        executa a ação contínua de desenho.
        Função executada ao movimentar o mouse enquanto o botão é pressionado.

        Args:
            event (tk.Event): evento de movimento do mouse.
        """
        string_data = ''

        if self.start_x is None or self.start_y is None:
            return

        if self.tool in ["pen", "eraser"]:
            string_data = self.draw_line(x, y)
            msg = ":".join(string_data)
            if self.peer:
                self.peer.envia_mensagem(msg)

        elif self.tool in ["line", "rectangle", "circle"]:
            if self.id_last_shape:
                self.canvas.delete(self.id_last_shape)
            self.draw_shapes(x, y)

    def end_action(self, event):
        """
        finaliza a ação de desenho.
        Função executada ao liberar o botão esquerdo do mouse

        Args:
            event (tk.Event): evento de soltar o botão.
        """
        x, y = event.x, event.y
        string_data = ""
        if self.start_x is None or self.start_y is None: # No drawing started
            return

        if self.tool in ["pen", "eraser"]:
            pass # Handled in perform_action
        elif self.tool in ["line", "rectangle", "circle"]:
            self.canvas.delete(self.id_last_shape)
            string_data = self.draw_shapes(x, y)
            msg = ":".join(string_data)
            self.id_last_shape = None
            if self.peer:
                self.peer.envia_mensagem(msg)

        elif self.tool == "text":
            pass


        self.start_x, self.start_y = None, None

    def _finalize_text(self, event):
        """
        finaliza a inserção de texto no canvas e envia para o peer.

        Args:
            event (tk.Event): evento pressionar Enter.
        """
        if not self.text_entry_widget:
            return
        msg = ""
        x, y = "", ""
        text_content = self.text_entry_widget.get()
        if text_content:

            bbox = self.canvas.bbox(self.text_entry_canvas_id)
            if bbox:
                x, y = bbox[0], bbox[1]

                font_size = max(8, self.pen_size)


                self.canvas.create_text(x, y, text=text_content, anchor=tk.NW,
                                        font=(self.text_font, font_size), fill=self.text_color,
                                        tags="drawn_item")
                string_data = [str(self.tool), str(self.pen_color), str(font_size), str(x), str(y), str(text_content)]
                msg = ":".join(string_data)

                if self.peer:
                    self.peer.envia_mensagem(msg)

            self._cleanup_temp_tools()


    def _cancel_text_entry(self, event):
        """
        cancela a inserção de texto sem salvar.
        Função executada ao apertar esc enquanto ainda o texto não foi salvo,
        ou quando ainda existe o widget de texto e você tenta criar outro
        """
        self._cleanup_temp_tools()

    def clear_canvas(self):
        """
        limpa canvas.
        """
        self.canvas.delete("all")

    def send_clear(self):
        """
        envia comando de limpeza do canvas para o peer conectado.
        """
        msg = "clear"
        if self.peer:
            self.peer.envia_mensagem(msg)

    def draw_line(self, x, y):
        """
        desenha uma linha contínua (pincel ou borracha).

        Args:
            x (int): posição X atual do cursor.
            y (int): posição Y atual do cursor.
        """
        string_data = ""
        if self.tool == "pen":
            self.canvas.create_line(self.start_x, self.start_y, x, y,
                                    fill=self.pen_color, width=self.pen_size,
                                    capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")

            string_data = [self.tool, self.pen_color, str(self.pen_size), str(self.start_x), str(self.start_y), str(x),
                           str(y)]
            self.start_x, self.start_y = x, y
        elif self.tool == "eraser":
            self.canvas.create_line(self.start_x, self.start_y, x, y,
                                    fill="white", width=self.pen_size * 2,
                                    capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
            string_data = [self.tool, self.pen_color, str(self.pen_size), str(self.start_x), str(self.start_y), str(x),
                           str(y)]
            self.start_x, self.start_y = x, y
        return string_data

    def draw_shapes(self, x, y):
        """
        desenha figuras geométricas (linha, retângulo ou círculo).

        Args:
            x (int): posição X final.
            y (int): posição Y final.
        """
        string_data = ""
        bbox = [min(self.start_x, x), min(self.start_y, y), max(self.start_x, x), max(self.start_y, y)]

        if self.tool == "line":
            self.id_last_shape = self.canvas.create_line(self.start_x, self.start_y, x, y,
                                                         fill=self.pen_color, width=self.pen_size,
                                                         capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
            string_data = [self.tool, self.pen_color, str(self.pen_size), str(self.start_x), str(self.start_y),
                           str(x), str(y)]
        elif self.tool == "rectangle":
            self.id_last_shape = self.canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3],
                                                              outline=self.pen_color, width=self.pen_size,
                                                              tags="drawn_item")
            string_data = [self.tool, self.pen_color, str(self.pen_size), str(bbox[0]), str(bbox[1]),
                           str(bbox[2]), str(bbox[3])]
        elif self.tool == "circle":
            self.id_last_shape = self.canvas.create_oval(bbox[0], bbox[1], bbox[2], bbox[3],
                                                         outline=self.pen_color, width=self.pen_size, tags="drawn_item")
            string_data = [self.tool, self.pen_color, str(self.pen_size), str(bbox[0]), str(bbox[1]),
                           str(bbox[2]), str(bbox[3])]

        return string_data