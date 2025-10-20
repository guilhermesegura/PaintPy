import tkinter as tk
from tkinter import colorchooser,  messagebox

"""
Essa classe foi criada com auxílio de IA 
conforme descrito na sessão 7 da documentação
"""


class PaintUI:
    def __init__(self, root, drawing_tools, peer):
        """
        inicializa a interface principal do aplicativo de desenho.
        """
        self.root = root
        self.drawing_tools = drawing_tools
        self.canvas = None
        self.photo_image = None
        self.peer = peer
        self._setup_toolbar()
        self._setup_canvas()
        self._bind_events()

    def _setup_toolbar(self):
        """
        cria e configura a barra de ferramentas superior.
        """
        self.toolbar = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # botão para escolher a cor da ferramenta (pen, text, circle, rectangle e line)
        self.color_button = tk.Button(self.toolbar, text="Color", command=self._choose_color)
        self.color_button.pack(side=tk.LEFT, padx=5, pady=5)

        # slider para escolher o tamanho / grossura da ferramenta
        self.size_label = tk.Label(self.toolbar, text="Size:")
        self.size_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.size_slider = tk.Scale(self.toolbar, from_=1, to=72, orient=tk.HORIZONTAL, # Definição da escala (tamanho máx = 72, tamanho min = 1)
                                    command=lambda s: self.drawing_tools.set_size(s))
        self.size_slider.set(self.drawing_tools.pen_size)
        self.size_slider.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Frame(self.toolbar, width=1, bg="grey", height=30).pack(side=tk.LEFT, padx=10)

        # botões da interface para escolher a ferramenta
        self.pen_button = tk.Button(self.toolbar, text="Pen", command=lambda: self.drawing_tools.set_tool("pen"))
        self.pen_button.pack(side=tk.LEFT, padx=2, pady=5)

        self.eraser_button = tk.Button(self.toolbar, text="Eraser", command=lambda: self.drawing_tools.set_tool("eraser"))
        self.eraser_button.pack(side=tk.LEFT, padx=2, pady=5)

        self.line_button = tk.Button(self.toolbar, text="Line", command=lambda: self.drawing_tools.set_tool("line"))
        self.line_button.pack(side=tk.LEFT, padx=2, pady=5)

        self.rect_button = tk.Button(self.toolbar, text="Rectangle", command=lambda: self.drawing_tools.set_tool("rectangle"))
        self.rect_button.pack(side=tk.LEFT, padx=2, pady=5)

        self.circle_button = tk.Button(self.toolbar, text="Circle", command=lambda: self.drawing_tools.set_tool("circle"))
        self.circle_button.pack(side=tk.LEFT, padx=2, pady=5)

        self.text_button = tk.Button(self.toolbar, text="Text", command=lambda: self.drawing_tools.set_tool("text"))
        self.text_button.pack(side=tk.LEFT, padx=2, pady=5)

        tk.Frame(self.toolbar, width=1, bg="grey", height=30).pack(side=tk.LEFT, padx=10)

        self.clear_button = tk.Button(self.toolbar, text="Clear", command=self._clear_canvas)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)

    def _setup_canvas(self):
        """
        cria e configura a área de desenho (canvas).
        """
        self.canvas = tk.Canvas(self.root, bg="white", bd=5, relief=tk.SUNKEN) # Define a tela branca do canvas
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.update_idletasks()

        initial_width = max(1, self.canvas.winfo_width())
        initial_height = max(1, self.canvas.winfo_height())


    def _bind_events(self):
        """
        vincula os eventos do mouse às funções correspondentes nas ferramentas de desenho.
        """
        self.canvas.bind("<Button-1>", self.drawing_tools.start_action)
        self.canvas.bind("<B1-Motion>", self.drawing_tools.perform_action)
        self.canvas.bind("<ButtonRelease-1>", self.drawing_tools.end_action)
        #self.root.bind("<Configure>", self._on_resize)

    def _choose_color(self):
        """
        abre a janela de seleção de cores.
        """
        color_code = colorchooser.askcolor(title="Choose pen/text color")
        if color_code[1]:
            self.drawing_tools.set_color(color_code[1])

    def _clear_canvas(self):
        """
        limpa todo conteúdo do canvas
        """
        resposta = messagebox.askyesno(title="Limpar", message="Deseja Limpar o Canvas?")
        if resposta:
            self.drawing_tools.clear_canvas()
            if self.peer:
                self.drawing_tools.send_clear()