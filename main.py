import tkinter as tk
from ui import PaintUI
from drawing_tools import DrawingTools

"""
Essa classe foi criada com auxílio de IA
conforme descrito na sessão 7 da documentação
"""

# variável global usada para manter referência da instância principal do aplicativo
app_instance = None

class PaintApp:
    def __init__(self, root, peer):
        """
       inicializa a aplicação.
       :param root: janela principal do Tkinter.
       :param peer: objeto responsável pela comunicação em rede (pode ser None se rodando localmente).
       """
        self.root = root
        self.root.title("Paint Colaborativo")
        self.root.geometry("800x600")
        self.root.resizable(True, True)


        self.drawing_tools = DrawingTools(None, peer)

        # cria a interface gráfica (menus, botões, área de desenho, etc.)
        self.ui = PaintUI(root, self.drawing_tools, peer)

        # agora que o canvas foi criado pelo UI, associamos ao DrawingTools
        self.drawing_tools.canvas = self.ui.canvas

        # define a ferramenta inicial de desenho
        self.drawing_tools.set_tool("pen")


def main(peer=None):
    """
    função principal que inicializa e executa o aplicativo.
    :param peer: objeto opcional de rede usado para sincronizar desenhos entre os usuários.
    """
    root = tk.Tk()
    app_instance = PaintApp(root, peer)
    if peer:
        peer.drawingTools = app_instance.drawing_tools
    root.mainloop()
    print("Terminou a main")
    if peer:
        peer.envia_mensagem(f"fechar: Fechou a conexao")

if __name__ == "__main__":
    main()