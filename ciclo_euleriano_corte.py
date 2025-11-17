"""
Programa para resolver o problema de Operação de máquinas que fazem cortes contínuos
usando o conceito de Ciclos Eulerianos.

Um ciclo euleriano é um caminho que visita cada aresta exatamente uma vez e retorna ao vértice inicial.
Isso é ideal para máquinas de corte contínuo (CNC, laser, usinagem) pois minimiza o tempo de corte.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from collections import defaultdict
import json


class GrafoEuleriano:
    """Classe para representar e manipular grafos e encontrar ciclos eulerianos."""
    
    def __init__(self):
        self.grafo = nx.MultiGraph()
        self.vertices = {}
        self.arestas = []
        
    def adicionar_vertice(self, nome, x, y):
        """Adiciona um vértice ao grafo."""
        self.grafo.add_node(nome, pos=(x, y))
        self.vertices[nome] = (x, y)
        
    def adicionar_aresta(self, origem, destino, peso=1):
        """Adiciona uma aresta ao grafo."""
        self.grafo.add_edge(origem, destino, weight=peso)
        self.arestas.append((origem, destino))
        
    def remover_vertice(self, nome):
        """Remove um vértice do grafo."""
        if nome in self.grafo:
            self.grafo.remove_node(nome)
            if nome in self.vertices:
                del self.vertices[nome]
            self.arestas = [(o, d) for o, d in self.arestas if o != nome and d != nome]
            
    def remover_aresta(self, origem, destino):
        """Remove uma aresta do grafo."""
        if self.grafo.has_edge(origem, destino):
            self.grafo.remove_edge(origem, destino)
            if (origem, destino) in self.arestas:
                self.arestas.remove((origem, destino))
            elif (destino, origem) in self.arestas:
                self.arestas.remove((destino, origem))
                
    def verificar_euleriano(self):
        """
        Verifica se o grafo possui um ciclo euleriano.
        Um grafo possui ciclo euleriano se e somente se:
        1. O grafo é conexo
        2. Todos os vértices têm grau par
        """
        if len(self.grafo.nodes()) == 0:
            return False, "Grafo vazio"
            
        if not nx.is_connected(self.grafo.to_undirected()):
            return False, "Grafo não é conexo"
            
        graus_impares = [v for v in self.grafo.nodes() if self.grafo.degree(v) % 2 != 0]
        if len(graus_impares) > 0:
            return False, f"Vértices com grau ímpar: {graus_impares}"
            
        return True, "Grafo é euleriano"
        
    def encontrar_ciclo_euleriano(self):
        """
        Encontra um ciclo euleriano usando o algoritmo de Hierholzer.
        Retorna uma lista de vértices representando o ciclo.
        """
        if len(self.grafo.edges()) == 0:
            return []
            
        # Cria uma cópia do grafo para não modificar o original
        grafo_temp = self.grafo.copy()
        
        # Escolhe um vértice inicial
        vertice_atual = list(grafo_temp.nodes())[0]
        ciclo = [vertice_atual]
        
        # Enquanto houver arestas não visitadas
        while grafo_temp.number_of_edges() > 0:
            # Encontra um ciclo a partir do vértice atual
            ciclo_parcial = self._encontrar_ciclo_parcial(grafo_temp, vertice_atual)
            
            # Insere o ciclo parcial no ciclo principal
            indice = ciclo.index(vertice_atual)
            ciclo = ciclo[:indice] + ciclo_parcial + ciclo[indice+1:]
            
            # Encontra o próximo vértice com arestas não visitadas
            vertice_atual = None
            for v in ciclo:
                if grafo_temp.degree(v) > 0:
                    vertice_atual = v
                    break
                    
            if vertice_atual is None:
                break
                
        return ciclo
        
    def _encontrar_ciclo_parcial(self, grafo, vertice_inicial):
        """Encontra um ciclo parcial a partir de um vértice."""
        ciclo = [vertice_inicial]
        vertice_atual = vertice_inicial
        
        while True:
            vizinhos = list(grafo.neighbors(vertice_atual))
            if not vizinhos:
                break
                
            proximo = vizinhos[0]
            ciclo.append(proximo)
            
            # Remove a aresta
            grafo.remove_edge(vertice_atual, proximo)
            
            if proximo == vertice_inicial:
                break
                
            vertice_atual = proximo
            
        return ciclo
        
    def calcular_distancia_total(self, caminho):
        """Calcula a distância total percorrida no caminho."""
        distancia_total = 0
        for i in range(len(caminho) - 1):
            v1 = self.vertices[caminho[i]]
            v2 = self.vertices[caminho[i+1]]
            distancia = ((v1[0] - v2[0])**2 + (v1[1] - v2[1])**2)**0.5
            distancia_total += distancia
        return distancia_total


class InterfaceCorteEuleriano:
    """Interface gráfica para o problema de corte contínuo usando ciclos eulerianos."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ Sistema de Otimização de Corte Contínuo (CNC/Laser)")
        self.root.geometry("1500x950")
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.grafo = GrafoEuleriano()
        self.ciclo_euleriano = []
        self.modo_edicao = "ponto_corte"  # "ponto_corte" ou "trajetoria"
        self.ponto_selecionado = None
        self.velocidade_corte = 100.0  # mm/min
        self.tempo_setup = 0.5  # minutos
        
        self.criar_interface()
        self.atualizar_visualizacao()
        self.atualizar_instrucoes()
        
    def criar_interface(self):
        """Cria a interface gráfica."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Painel de controles (esquerda)
        painel_controles = ttk.LabelFrame(main_frame, text="🎛️ Painel de Controle da Máquina", padding="10")
        painel_controles.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        painel_controles.columnconfigure(0, weight=1)
        
        # Modo de operação da máquina
        frame_modo = ttk.LabelFrame(painel_controles, text="🔧 Modo de Operação", padding="8")
        frame_modo.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame_modo.columnconfigure(0, weight=1)
        
        self.modo_var = tk.StringVar(value="ponto_corte")
        
        # Botões de modo
        self.btn_modo_ponto = ttk.Radiobutton(
            frame_modo, 
            text="📍 Definir Pontos de Corte", 
            variable=self.modo_var, 
            value="ponto_corte", 
            command=self.alterar_modo
        )
        self.btn_modo_ponto.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=3)
        
        self.btn_modo_trajetoria = ttk.Radiobutton(
            frame_modo, 
            text="✂️ Definir Trajetórias de Corte", 
            variable=self.modo_var, 
            value="trajetoria", 
            command=self.alterar_modo
        )
        self.btn_modo_trajetoria.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=3)
        
        # Indicador visual do modo atual
        self.label_modo_atual = ttk.Label(
            frame_modo, 
            text="Modo: Definir Pontos de Corte", 
            foreground="green",
            font=("Arial", 9, "bold")
        )
        self.label_modo_atual.grid(row=2, column=0, pady=(5, 0))
        
        # Definir pontos de corte manualmente
        frame_ponto_manual = ttk.LabelFrame(painel_controles, text="📍 Coordenadas do Ponto de Corte", padding="8")
        frame_ponto_manual.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame_ponto_manual.columnconfigure(1, weight=1)
        
        ttk.Label(frame_ponto_manual, text="ID Ponto:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.entry_nome = ttk.Entry(frame_ponto_manual, width=12)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        self.entry_nome.bind('<Return>', lambda e: self.adicionar_ponto_corte_manual())
        
        ttk.Label(frame_ponto_manual, text="X (mm):").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.entry_x = ttk.Entry(frame_ponto_manual, width=12)
        self.entry_x.grid(row=1, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        self.entry_x.bind('<Return>', lambda e: self.adicionar_ponto_corte_manual())
        
        ttk.Label(frame_ponto_manual, text="Y (mm):").grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.entry_y = ttk.Entry(frame_ponto_manual, width=12)
        self.entry_y.grid(row=2, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        self.entry_y.bind('<Return>', lambda e: self.adicionar_ponto_corte_manual())
        
        btn_add_ponto = ttk.Button(frame_ponto_manual, text="📍 Adicionar Ponto", command=self.adicionar_ponto_corte_manual)
        btn_add_ponto.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Definir trajetória de corte manualmente
        frame_trajetoria_manual = ttk.LabelFrame(painel_controles, text="✂️ Trajetória de Corte", padding="8")
        frame_trajetoria_manual.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame_trajetoria_manual.columnconfigure(1, weight=1)
        
        ttk.Label(frame_trajetoria_manual, text="Ponto Inicial:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.entry_origem = ttk.Entry(frame_trajetoria_manual, width=12)
        self.entry_origem.grid(row=0, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        self.entry_origem.bind('<Return>', lambda e: self.adicionar_trajetoria_manual())
        
        ttk.Label(frame_trajetoria_manual, text="Ponto Final:").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.entry_destino = ttk.Entry(frame_trajetoria_manual, width=12)
        self.entry_destino.grid(row=1, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        self.entry_destino.bind('<Return>', lambda e: self.adicionar_trajetoria_manual())
        
        btn_add_trajetoria = ttk.Button(frame_trajetoria_manual, text="✂️ Adicionar Trajetória", command=self.adicionar_trajetoria_manual)
        btn_add_trajetoria.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Parâmetros da máquina
        frame_parametros = ttk.LabelFrame(painel_controles, text="⚙️ Parâmetros da Máquina", padding="8")
        frame_parametros.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame_parametros.columnconfigure(1, weight=1)
        
        ttk.Label(frame_parametros, text="Velocidade (mm/min):").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.entry_velocidade = ttk.Entry(frame_parametros, width=12)
        self.entry_velocidade.insert(0, "100.0")
        self.entry_velocidade.grid(row=0, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        self.entry_velocidade.bind('<Return>', lambda e: self.atualizar_velocidade())
        
        ttk.Label(frame_parametros, text="Tempo Setup (min):").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.entry_setup = ttk.Entry(frame_parametros, width=12)
        self.entry_setup.insert(0, "0.5")
        self.entry_setup.grid(row=1, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        self.entry_setup.bind('<Return>', lambda e: self.atualizar_setup())
        
        # Botões de ação principais
        frame_acoes = ttk.LabelFrame(painel_controles, text="🎯 Operações da Máquina", padding="8")
        frame_acoes.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame_acoes.columnconfigure(0, weight=1)
        
        self.btn_otimizar = ttk.Button(
            frame_acoes, 
            text="🚀 Otimizar Caminho da Ferramenta", 
            command=self.otimizar_caminho
        )
        self.btn_otimizar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=3)
        
        btn_limpar = ttk.Button(
            frame_acoes, 
            text="🗑️ Limpar Projeto", 
            command=self.limpar_projeto
        )
        btn_limpar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=3)
        
        btn_remover = ttk.Button(
            frame_acoes, 
            text="➖ Remover Último Ponto", 
            command=self.remover_ultimo_ponto
        )
        btn_remover.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=3)
        
        # Exemplos de peças pré-definidas
        frame_exemplos = ttk.LabelFrame(painel_controles, text="📦 Peças Pré-definidas", padding="8")
        frame_exemplos.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame_exemplos.columnconfigure(0, weight=1)
        
        ttk.Button(
            frame_exemplos, 
            text="⬜ Placa Retangular", 
            command=self.exemplo_placa_retangular
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Button(
            frame_exemplos, 
            text="⭐ Peça em Estrela", 
            command=self.exemplo_peca_estrela
        ).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Button(
            frame_exemplos, 
            text="🔷 Grade com Furos", 
            command=self.exemplo_grade_furos
        ).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Salvar/Carregar
        frame_arquivo = ttk.LabelFrame(painel_controles, text="💾 Arquivo", padding="8")
        frame_arquivo.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame_arquivo.columnconfigure(0, weight=1)
        
        ttk.Button(
            frame_arquivo, 
            text="💾 Salvar Grafo", 
            command=self.salvar_grafo
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Button(
            frame_arquivo, 
            text="📂 Carregar Grafo", 
            command=self.carregar_grafo
        ).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Informações do projeto
        frame_info = ttk.LabelFrame(painel_controles, text="📊 Status do Projeto", padding="8")
        frame_info.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        frame_info.columnconfigure(0, weight=1)
        
        self.label_info = ttk.Label(
            frame_info, 
            text="Pontos de Corte: 0\nTrajetórias: 0", 
            wraplength=200, 
            justify=tk.LEFT,
            font=("Arial", 9)
        )
        self.label_info.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Informações de tempo e distância
        self.label_tempo = ttk.Label(
            frame_info, 
            text="", 
            wraplength=200, 
            justify=tk.LEFT,
            font=("Arial", 9, "bold"),
            foreground="blue"
        )
        self.label_tempo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Barra de status/instruções
        frame_status = ttk.LabelFrame(painel_controles, text="💡 Instruções", padding="8")
        frame_status.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame_status.columnconfigure(0, weight=1)
        painel_controles.rowconfigure(7, weight=1)
        
        self.label_instrucoes = ttk.Label(
            frame_status, 
            text="", 
            wraplength=200, 
            justify=tk.LEFT,
            font=("Arial", 8),
            foreground="gray"
        )
        self.label_instrucoes.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N))
        
        # Área de visualização (direita) - Mesa de trabalho
        frame_visualizacao = ttk.LabelFrame(main_frame, text="🖥️ Mesa de Trabalho - Visualização da Peça", padding="10")
        frame_visualizacao.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame_visualizacao.columnconfigure(0, weight=1)
        frame_visualizacao.rowconfigure(0, weight=1)
        
        # Criar figura matplotlib com estilo melhorado
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except:
            try:
                plt.style.use('seaborn-darkgrid')
            except:
                pass  # Usa estilo padrão
        self.fig, self.ax = plt.subplots(figsize=(11, 8), facecolor='white')
        self.fig.patch.set_facecolor('white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_visualizacao)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Conectar eventos do mouse
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        
        # Área de resultados (embaixo) - Programa CNC
        frame_resultados = ttk.LabelFrame(main_frame, text="📋 Programa CNC - Caminho Otimizado da Ferramenta", padding="10")
        frame_resultados.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        frame_resultados.columnconfigure(0, weight=1)
        frame_resultados.rowconfigure(0, weight=1)
        
        self.text_resultados = tk.Text(
            frame_resultados, 
            height=6, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#d4d4d4",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.text_resultados.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(frame_resultados, orient=tk.VERTICAL, command=self.text_resultados.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text_resultados.configure(yscrollcommand=scrollbar.set)
        
        # Mensagem inicial
        self.text_resultados.insert(tk.END, "╔═══════════════════════════════════════════════════════════╗\n")
        self.text_resultados.insert(tk.END, "║  Sistema de Otimização de Corte Contínuo                  ║\n")
        self.text_resultados.insert(tk.END, "║  Aguardando definição dos pontos de corte...              ║\n")
        self.text_resultados.insert(tk.END, "╚═══════════════════════════════════════════════════════════╝\n\n")
        self.text_resultados.insert(tk.END, "INSTRUÇÕES:\n")
        self.text_resultados.insert(tk.END, "1. Defina os pontos de corte na peça\n")
        self.text_resultados.insert(tk.END, "2. Defina as trajetórias de corte entre os pontos\n")
        self.text_resultados.insert(tk.END, "3. Clique em 'Otimizar Caminho da Ferramenta' para gerar o programa CNC")
        self.text_resultados.config(state=tk.DISABLED)
        
    def alterar_modo(self):
        """Altera o modo de operação da máquina."""
        self.modo_edicao = self.modo_var.get()
        self.ponto_selecionado = None
        
        # Atualizar indicador visual
        if self.modo_edicao == "ponto_corte":
            self.label_modo_atual.config(text="Modo: 📍 Definir Pontos de Corte", foreground="green")
        else:
            self.label_modo_atual.config(text="Modo: ✂️ Definir Trajetórias de Corte", foreground="blue")
            
        self.atualizar_instrucoes()
        self.atualizar_visualizacao()
    
    def atualizar_velocidade(self):
        """Atualiza a velocidade de corte."""
        try:
            self.velocidade_corte = float(self.entry_velocidade.get())
            self.atualizar_info()
        except ValueError:
            messagebox.showerror("Erro", "Velocidade inválida!")
            self.entry_velocidade.delete(0, tk.END)
            self.entry_velocidade.insert(0, str(self.velocidade_corte))
    
    def atualizar_setup(self):
        """Atualiza o tempo de setup."""
        try:
            self.tempo_setup = float(self.entry_setup.get())
        except ValueError:
            messagebox.showerror("Erro", "Tempo de setup inválido!")
            self.entry_setup.delete(0, tk.END)
            self.entry_setup.insert(0, str(self.tempo_setup))
        
    def on_click(self, event):
        """Manipula cliques na mesa de trabalho."""
        if event.inaxes != self.ax:
            return
            
        x, y = event.xdata, event.ydata
        
        if self.modo_edicao == "ponto_corte":
            # Adicionar ponto de corte na posição clicada
            nome = f"P{len(self.grafo.vertices) + 1}"
            self.grafo.adicionar_vertice(nome, x, y)
            self.atualizar_visualizacao()
            self.atualizar_instrucoes()
        elif self.modo_edicao == "trajetoria":
            # Encontrar ponto mais próximo
            ponto_proximo = self.encontrar_ponto_proximo(x, y)
            if ponto_proximo:
                if self.ponto_selecionado is None:
                    self.ponto_selecionado = ponto_proximo
                    self.atualizar_visualizacao()
                    self.atualizar_instrucoes()
                else:
                    if self.ponto_selecionado != ponto_proximo:
                        self.grafo.adicionar_aresta(self.ponto_selecionado, ponto_proximo)
                        self.ponto_selecionado = None
                        self.atualizar_visualizacao()
                        self.atualizar_instrucoes()
                    else:
                        # Clicou no mesmo ponto, deseleciona
                        self.ponto_selecionado = None
                        self.atualizar_visualizacao()
                        self.atualizar_instrucoes()
            else:
                # Clicou longe de qualquer ponto, deseleciona
                if self.ponto_selecionado:
                    self.ponto_selecionado = None
                    self.atualizar_visualizacao()
                    self.atualizar_instrucoes()
                    
    def encontrar_ponto_proximo(self, x, y, limite=0.2):
        """Encontra o ponto de corte mais próximo de uma coordenada."""
        menor_distancia = float('inf')
        ponto_proximo = None
        
        for nome, (vx, vy) in self.grafo.vertices.items():
            distancia = ((x - vx)**2 + (y - vy)**2)**0.5
            if distancia < menor_distancia and distancia < limite:
                menor_distancia = distancia
                ponto_proximo = nome
                
        return ponto_proximo
    
    def on_hover(self, event):
        """Manipula movimento do mouse sobre a mesa de trabalho."""
        if event.inaxes != self.ax:
            return
            
        if self.modo_edicao == "trajetoria" and len(self.grafo.vertices) > 0:
            x, y = event.xdata, event.ydata
            ponto_proximo = self.encontrar_ponto_proximo(x, y, limite=0.3)
            if ponto_proximo:
                self.ax.set_title(f'Mesa de Trabalho - Próximo ao ponto: {ponto_proximo}', 
                                 color='blue', fontweight='bold')
            else:
                self.ax.set_title('Mesa de Trabalho - Visualização da Peça', color='black', fontweight='normal')
            self.canvas.draw_idle()
        
    def adicionar_ponto_corte_manual(self):
        """Adiciona um ponto de corte usando os campos de entrada."""
        try:
            nome = self.entry_nome.get() or f"P{len(self.grafo.vertices) + 1}"
            x = float(self.entry_x.get())
            y = float(self.entry_y.get())
            
            if nome in self.grafo.vertices:
                messagebox.showerror("Erro", f"Ponto '{nome}' já existe!")
                return
                
            self.grafo.adicionar_vertice(nome, x, y)
            self.entry_nome.delete(0, tk.END)
            self.entry_x.delete(0, tk.END)
            self.entry_y.delete(0, tk.END)
            self.atualizar_visualizacao()
            self.atualizar_info()
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos para coordenadas X e Y!")
            
    def adicionar_trajetoria_manual(self):
        """Adiciona uma trajetória de corte usando os campos de entrada."""
        origem = self.entry_origem.get()
        destino = self.entry_destino.get()
        
        if not origem or not destino:
            messagebox.showerror("Erro", "Informe ponto inicial e final!")
            return
            
        if origem not in self.grafo.vertices or destino not in self.grafo.vertices:
            messagebox.showerror("Erro", "Pontos de corte não encontrados!")
            return
            
        self.grafo.adicionar_aresta(origem, destino)
        self.entry_origem.delete(0, tk.END)
        self.entry_destino.delete(0, tk.END)
        self.atualizar_visualizacao()
        self.atualizar_info()
        
    def otimizar_caminho(self):
        """Otimiza o caminho da ferramenta usando ciclo euleriano."""
        if len(self.grafo.vertices) == 0:
            messagebox.showinfo("Atenção", "Defina pelo menos um ponto de corte primeiro!")
            return
            
        euleriano, mensagem = self.grafo.verificar_euleriano()
        
        if not euleriano:
            messagebox.showwarning("⚠️ Trajetória não Otimizável", 
                                 f"A configuração atual não permite corte contínuo!\n\n{mensagem}\n\n"
                                 "CONDIÇÕES PARA CORTE CONTÍNUO:\n"
                                 "• Todos os pontos devem estar conectados\n"
                                 "• Cada ponto deve ter número par de trajetórias\n\n"
                                 "Dica: Adicione trajetórias para tornar todos os pontos pares.")
            self.text_resultados.config(state=tk.NORMAL)
            self.text_resultados.delete(1.0, tk.END)
            self.text_resultados.insert(tk.END, f"╔═══════════════════════════════════════════════════════════╗\n")
            self.text_resultados.insert(tk.END, f"║  ❌ ERRO: {mensagem:47s}║\n")
            self.text_resultados.insert(tk.END, f"╚═══════════════════════════════════════════════════════════╝\n\n")
            self.text_resultados.insert(tk.END, "Ajuste a configuração dos pontos e trajetórias.\n")
            self.text_resultados.config(state=tk.DISABLED)
            return
            
        self.ciclo_euleriano = self.grafo.encontrar_ciclo_euleriano()
        
        if not self.ciclo_euleriano:
            self.text_resultados.config(state=tk.NORMAL)
            self.text_resultados.delete(1.0, tk.END)
            self.text_resultados.insert(tk.END, "Nenhum caminho otimizado encontrado.")
            self.text_resultados.config(state=tk.DISABLED)
            return
            
        # Calcular distância total e tempo
        distancia_total = self.grafo.calcular_distancia_total(self.ciclo_euleriano)
        tempo_corte = (distancia_total / self.velocidade_corte) if self.velocidade_corte > 0 else 0
        tempo_total = tempo_corte + self.tempo_setup
        
        # Gerar programa CNC formatado
        self.text_resultados.config(state=tk.NORMAL)
        self.text_resultados.delete(1.0, tk.END)
        
        resultado = "╔═══════════════════════════════════════════════════════════╗\n"
        resultado += "║  ✅ CAMINHO OTIMIZADO DA FERRAMENTA                    ║\n"
        resultado += "╚═══════════════════════════════════════════════════════════╝\n\n"
        resultado += "PROGRAMA CNC:\n"
        resultado += "─────────────────────────────────────────────────────────────\n"
        resultado += f"G00 X{self.grafo.vertices[self.ciclo_euleriano[0]][0]:.2f} Y{self.grafo.vertices[self.ciclo_euleriano[0]][1]:.2f}  ; Posicionamento inicial\n"
        resultado += f"G01 F{self.velocidade_corte:.1f}  ; Velocidade de corte\n\n"
        
        for i, ponto in enumerate(self.ciclo_euleriano[1:], 1):
            x, y = self.grafo.vertices[ponto]
            resultado += f"N{i:03d} G01 X{x:.2f} Y{y:.2f}  ; Corte até ponto {ponto}\n"
        
        resultado += f"\nG00 X{self.grafo.vertices[self.ciclo_euleriano[0]][0]:.2f} Y{self.grafo.vertices[self.ciclo_euleriano[0]][1]:.2f}  ; Retorno ao início\n"
        resultado += "M30  ; Fim do programa\n"
        resultado += "─────────────────────────────────────────────────────────────\n\n"
        resultado += "ESTATÍSTICAS DE PRODUÇÃO:\n"
        resultado += f"  • Distância total percorrida: {distancia_total:.2f} mm\n"
        resultado += f"  • Tempo de corte: {tempo_corte:.2f} min\n"
        resultado += f"  • Tempo de setup: {self.tempo_setup:.2f} min\n"
        resultado += f"  • Tempo total estimado: {tempo_total:.2f} min\n"
        resultado += f"  • Trajetórias percorridas: {len(self.ciclo_euleriano) - 1}\n\n"
        resultado += "💡 Este caminho visita cada trajetória exatamente uma vez,\n"
        resultado += "   minimizando o tempo de corte e movimentos desnecessários!"
        
        self.text_resultados.insert(tk.END, resultado)
        self.text_resultados.config(state=tk.DISABLED)
        
        self.atualizar_visualizacao()
        self.atualizar_info()
        
        messagebox.showinfo("✅ Otimização Concluída", 
                          f"Caminho otimizado encontrado!\n\n"
                          f"Distância: {distancia_total:.2f} mm\n"
                          f"Tempo estimado: {tempo_total:.2f} min\n\n"
                          f"O caminho está destacado em vermelho na mesa de trabalho.")
        
    def atualizar_visualizacao(self):
        """Atualiza a visualização da mesa de trabalho."""
        self.ax.clear()
        
        # Fundo da mesa (cinza claro)
        self.ax.set_facecolor('#f0f0f0')
        
        if len(self.grafo.vertices) == 0:
            self.ax.text(0.5, 0.5, 
                        "📍 Clique na mesa para definir pontos de corte\n\n"
                        "ou use uma peça pré-definida no painel esquerdo", 
                        ha='center', va='center', transform=self.ax.transAxes, 
                        fontsize=13, color='gray', style='italic',
                        bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.8, linewidth=2))
            self.ax.set_xlim(-1, 1)
            self.ax.set_ylim(-1, 1)
            self.canvas.draw()
            self.atualizar_info()
            return
            
        # Calcular limites da mesa
        if len(self.grafo.vertices) > 0:
            xs = [pos[0] for pos in self.grafo.vertices.values()]
            ys = [pos[1] for pos in self.grafo.vertices.values()]
            margin = max((max(xs) - min(xs)), (max(ys) - min(ys))) * 0.2 + 1
            self.ax.set_xlim(min(xs) - margin, max(xs) + margin)
            self.ax.set_ylim(min(ys) - margin, max(ys) + margin)
            
        # Desenhar trajetórias de corte definidas (cinza tracejado)
        for origem, destino in self.grafo.arestas:
            x1, y1 = self.grafo.vertices[origem]
            x2, y2 = self.grafo.vertices[destino]
            self.ax.plot([x1, x2], [y1, y2], 'gray', alpha=0.5, linewidth=2, linestyle='--', label='Trajetórias definidas')
            
        # Desenhar caminho otimizado da ferramenta (vermelho destacado)
        if self.ciclo_euleriano and len(self.ciclo_euleriano) > 1:
            for i in range(len(self.ciclo_euleriano) - 1):
                v1 = self.ciclo_euleriano[i]
                v2 = self.ciclo_euleriano[i + 1]
                x1, y1 = self.grafo.vertices[v1]
                x2, y2 = self.grafo.vertices[v2]
                self.ax.plot([x1, x2], [y1, y2], 'r-', linewidth=4, alpha=0.9, zorder=2, label='Caminho otimizado')
                
                # Número da etapa do programa CNC
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                self.ax.text(mid_x, mid_y, f"N{i+1}", ha='center', va='center',
                           fontsize=9, fontweight='bold', color='red',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                                   edgecolor='red', linewidth=2, alpha=0.9), zorder=3)
                
            # Desenhar setas indicando direção da ferramenta
            for i in range(len(self.ciclo_euleriano) - 1):
                v1 = self.ciclo_euleriano[i]
                v2 = self.ciclo_euleriano[i + 1]
                x1, y1 = self.grafo.vertices[v1]
                x2, y2 = self.grafo.vertices[v2]
                dx = x2 - x1
                dy = y2 - y1
                comprimento = (dx**2 + dy**2)**0.5
                if comprimento > 0.1:
                    self.ax.arrow(x1 + dx*0.5, y1 + dy*0.5, dx*0.15, dy*0.15,
                                head_width=0.2, head_length=0.2, fc='red', ec='red', 
                                alpha=0.9, zorder=4)
                    
        # Desenhar pontos de corte
        for nome, (x, y) in self.grafo.vertices.items():
            # Cor diferente para ponto selecionado
            if nome == self.ponto_selecionado:
                cor = '#FF4444'  # Vermelho para selecionado
                tamanho = 18
                borda = 'darkred'
                largura_borda = 3
            elif nome in (self.ciclo_euleriano[0] if self.ciclo_euleriano else []):
                cor = '#00AA00'  # Verde para início do ciclo
                tamanho = 14
                borda = 'darkgreen'
                largura_borda = 2.5
            else:
                cor = '#0066CC'  # Azul para pontos normais
                tamanho = 12
                borda = 'darkblue'
                largura_borda = 2
                
            # Desenhar ponto de corte
            self.ax.plot(x, y, 'o', color=cor, markersize=tamanho, 
                        markeredgecolor=borda, markeredgewidth=largura_borda, zorder=5)
            # Label do ponto
            self.ax.text(x, y + 0.25, nome, ha='center', va='bottom', 
                        fontsize=10, fontweight='bold', color='black',
                        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                                edgecolor=borda, alpha=0.9, linewidth=1.5), zorder=6)
            
        # Título com informações
        titulo = 'Mesa de Trabalho - Visualização da Peça'
        if self.ponto_selecionado:
            titulo += f' | Ponto selecionado: {self.ponto_selecionado}'
        if self.ciclo_euleriano:
            titulo += ' | Caminho otimizado ativo'
            
        self.ax.set_xlabel('Coordenada X (mm)', fontsize=11, fontweight='bold')
        self.ax.set_ylabel('Coordenada Y (mm)', fontsize=11, fontweight='bold')
        self.ax.set_title(titulo, fontsize=13, fontweight='bold', pad=15)
        self.ax.grid(True, alpha=0.4, linestyle=':', linewidth=0.8, color='gray')
        self.ax.set_aspect('equal', adjustable='box')
        
        # Legenda
        if len(self.grafo.arestas) > 0 or self.ciclo_euleriano:
            self.ax.plot([], [], 'b-', linewidth=2, label='Pontos de corte')
            if self.ciclo_euleriano:
                self.ax.plot([], [], 'r-', linewidth=4, label='Caminho otimizado')
            self.ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
        
        self.canvas.draw()
        self.atualizar_info()
        
    def atualizar_info(self):
        """Atualiza as informações do projeto."""
        num_pontos = len(self.grafo.vertices)
        num_trajetorias = len(self.grafo.arestas)
        
        info = f"📊 Status do Projeto:\n"
        info += f"   Pontos de corte: {num_pontos}\n"
        info += f"   Trajetórias: {num_trajetorias}\n"
        
        if num_pontos > 0:
            euleriano, mensagem = self.grafo.verificar_euleriano()
            status_icon = "✅" if euleriano else "⚠️"
            status_text = "Pronto para otimizar" if euleriano else "Ajuste necessário"
            info += f"\n{status_icon} {status_text}:\n   {mensagem}"
            
            # Mostrar graus dos pontos (número de trajetórias por ponto)
            if num_pontos <= 10:
                info += f"\n\n📐 Trajetórias por ponto:"
                for nome in sorted(self.grafo.vertices.keys()):
                    grau = self.grafo.grafo.degree(nome)
                    paridade = "✓" if grau % 2 == 0 else "✗"
                    info += f"\n   {nome}: {grau} {paridade}"
            
        self.label_info.config(text=info)
        
        # Atualizar informações de tempo e distância
        if self.ciclo_euleriano and len(self.ciclo_euleriano) > 1:
            distancia = self.grafo.calcular_distancia_total(self.ciclo_euleriano)
            tempo_corte = (distancia / self.velocidade_corte) if self.velocidade_corte > 0 else 0
            tempo_total = tempo_corte + self.tempo_setup
            
            tempo_info = f"⏱️ Tempo Estimado:\n"
            tempo_info += f"   Corte: {tempo_corte:.2f} min\n"
            tempo_info += f"   Total: {tempo_total:.2f} min\n"
            tempo_info += f"   Distância: {distancia:.2f} mm"
            self.label_tempo.config(text=tempo_info)
        else:
            self.label_tempo.config(text="")
    
    def atualizar_instrucoes(self):
        """Atualiza as instruções contextuais."""
        if self.modo_edicao == "ponto_corte":
            instrucoes = "💡 INSTRUÇÕES:\n\n"
            instrucoes += "1. Clique na mesa para definir\n   um ponto de corte\n"
            instrucoes += "2. Ou use os campos acima para\n   especificar coordenadas (mm)\n"
            instrucoes += "3. Defina pelo menos 2 pontos\n   para começar"
        else:  # modo trajetoria
            if self.ponto_selecionado is None:
                instrucoes = "💡 INSTRUÇÕES:\n\n"
                instrucoes += "1. Clique em um ponto para\n   selecioná-lo\n"
                instrucoes += "2. Depois clique em outro\n   ponto para definir trajetória\n"
                instrucoes += "3. Ou use os campos acima\n   para especificar pontos"
            else:
                instrucoes = f"💡 INSTRUÇÕES:\n\n"
                instrucoes += f"Ponto '{self.ponto_selecionado}'\n"
                instrucoes += "selecionado!\n\n"
                instrucoes += "Clique em outro ponto para\n"
                instrucoes += "criar trajetória de corte\n"
                instrucoes += "ou clique fora para cancelar"
                
        self.label_instrucoes.config(text=instrucoes)
        
    def limpar_projeto(self):
        """Limpa o projeto atual."""
        if messagebox.askyesno("🗑️ Confirmar Limpeza", 
                             "Deseja realmente limpar todo o projeto?\n\n"
                             "Todos os pontos e trajetórias serão removidos.\n"
                             "Esta ação não pode ser desfeita."):
            self.grafo = GrafoEuleriano()
            self.ciclo_euleriano = []
            self.ponto_selecionado = None
            self.text_resultados.config(state=tk.NORMAL)
            self.text_resultados.delete(1.0, tk.END)
            self.text_resultados.insert(tk.END, "╔═══════════════════════════════════════════════════════════╗\n")
            self.text_resultados.insert(tk.END, "║  Projeto limpo. Defina novos pontos de corte...         ║\n")
            self.text_resultados.insert(tk.END, "╚═══════════════════════════════════════════════════════════╝")
            self.text_resultados.config(state=tk.DISABLED)
            self.atualizar_visualizacao()
            self.atualizar_instrucoes()
            self.atualizar_info()
            
    def remover_ultimo_ponto(self):
        """Remove o último ponto de corte adicionado."""
        if len(self.grafo.vertices) == 0:
            messagebox.showinfo("Info", "Não há pontos de corte para remover.")
            return
            
        pontos = list(self.grafo.vertices.keys())
        if pontos:
            self.grafo.remover_vertice(pontos[-1])
            self.ponto_selecionado = None
            self.atualizar_visualizacao()
            self.atualizar_info()
            
    def exemplo_placa_retangular(self):
        """Cria um exemplo: placa retangular com corte no perímetro."""
        self.grafo = GrafoEuleriano()
        self.ciclo_euleriano = []
        self.ponto_selecionado = None
        
        # Pontos de corte formando um retângulo
        self.grafo.adicionar_vertice("P1", 0, 0)
        self.grafo.adicionar_vertice("P2", 50, 0)
        self.grafo.adicionar_vertice("P3", 50, 30)
        self.grafo.adicionar_vertice("P4", 0, 30)
        
        # Trajetórias de corte (perímetro)
        self.grafo.adicionar_aresta("P1", "P2")
        self.grafo.adicionar_aresta("P2", "P3")
        self.grafo.adicionar_aresta("P3", "P4")
        self.grafo.adicionar_aresta("P4", "P1")
        
        self.atualizar_visualizacao()
        self.atualizar_instrucoes()
        self.atualizar_info()
        
    def exemplo_peca_estrela(self):
        """Cria um exemplo: peça em formato de estrela."""
        self.grafo = GrafoEuleriano()
        self.ciclo_euleriano = []
        self.ponto_selecionado = None
        import math
        
        centro_x, centro_y = 25, 25
        raio_externo = 20
        raio_interno = 10
        
        # Pontos externos da estrela
        pontos_externos = []
        for i in range(5):
            angulo = 2 * math.pi * i / 5 - math.pi/2
            x = centro_x + raio_externo * math.cos(angulo)
            y = centro_y + raio_externo * math.sin(angulo)
            nome = f"E{i+1}"
            self.grafo.adicionar_vertice(nome, x, y)
            pontos_externos.append(nome)
            
        # Pontos internos da estrela
        pontos_internos = []
        for i in range(5):
            angulo = 2 * math.pi * i / 5 - math.pi/2 + math.pi/5
            x = centro_x + raio_interno * math.cos(angulo)
            y = centro_y + raio_interno * math.sin(angulo)
            nome = f"I{i+1}"
            self.grafo.adicionar_vertice(nome, x, y)
            pontos_internos.append(nome)
            
        # Trajetórias formando a estrela
        for i in range(5):
            self.grafo.adicionar_aresta(pontos_externos[i], pontos_internos[i])
            self.grafo.adicionar_aresta(pontos_internos[i], pontos_externos[(i+1) % 5])
            
        self.atualizar_visualizacao()
        self.atualizar_instrucoes()
        self.atualizar_info()
        
    def exemplo_grade_furos(self):
        """Cria um exemplo: grade com padrão de furos."""
        self.grafo = GrafoEuleriano()
        self.ciclo_euleriano = []
        self.ponto_selecionado = None
        
        # Cria uma grade 3x3 de pontos de corte
        for i in range(3):
            for j in range(3):
                nome = f"P{i}{j}"
                self.grafo.adicionar_vertice(nome, i*20, j*20)
                
        # Conecta em grade (padrão de corte)
        for i in range(3):
            for j in range(3):
                nome = f"P{i}{j}"
                if i < 2:
                    self.grafo.adicionar_aresta(nome, f"P{i+1}{j}")
                if j < 2:
                    self.grafo.adicionar_aresta(nome, f"P{i}{j+1}")
                    
        # Conexões diagonais para garantir grau par
        self.grafo.adicionar_aresta("P00", "P22")
        self.grafo.adicionar_aresta("P02", "P20")
        
        self.atualizar_visualizacao()
        self.atualizar_instrucoes()
        self.atualizar_info()
        
    def salvar_grafo(self):
        """Salva o grafo em um arquivo JSON."""
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if arquivo:
            dados = {
                "vertices": {nome: {"x": pos[0], "y": pos[1]} 
                           for nome, pos in self.grafo.vertices.items()},
                "arestas": self.grafo.arestas
            }
            
            with open(arquivo, 'w') as f:
                json.dump(dados, f, indent=2)
                
            messagebox.showinfo("Sucesso", f"Grafo salvo em {arquivo}")
            
    def carregar_grafo(self):
        """Carrega um grafo de um arquivo JSON."""
        arquivo = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if arquivo:
            try:
                with open(arquivo, 'r') as f:
                    dados = json.load(f)
                    
                self.grafo = GrafoEuleriano()
                
                for nome, pos in dados["vertices"].items():
                    self.grafo.adicionar_vertice(nome, pos["x"], pos["y"])
                    
                for origem, destino in dados["arestas"]:
                    self.grafo.adicionar_aresta(origem, destino)
                    
                self.ciclo_euleriano = []
                self.vertice_selecionado = None
                self.atualizar_visualizacao()
                self.atualizar_instrucoes()
                messagebox.showinfo("✅ Sucesso", f"Grafo carregado de {arquivo}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")


def main():
    """Função principal."""
    root = tk.Tk()
    app = InterfaceCorteEuleriano(root)
    root.mainloop()


if __name__ == "__main__":
    main()

