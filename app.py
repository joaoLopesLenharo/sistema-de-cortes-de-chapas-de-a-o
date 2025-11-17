
"""
Sistema de Otimização de Corte Contínuo - Backend Flask
API REST para comunicação com interface web
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import networkx as nx
import json

app = Flask(__name__)
CORS(app)


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
        # Adicionar à lista apenas se não existir (evitar duplicatas na lista)
        if (origem, destino) not in self.arestas and (destino, origem) not in self.arestas:
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
        """Verifica se o grafo possui um ciclo euleriano."""
        if len(self.grafo.nodes()) == 0:
            return False, "Grafo vazio"
            
        if not nx.is_connected(self.grafo.to_undirected()):
            return False, "Grafo não é conexo"
            
        graus_impares = [v for v in self.grafo.nodes() if self.grafo.degree(v) % 2 != 0]
        if len(graus_impares) > 0:
            return False, f"Vértices com grau ímpar: {graus_impares}"
            
        return True, "Grafo é euleriano"
        
    def encontrar_ciclo_euleriano(self):
        """Encontra um ciclo euleriano usando o algoritmo de Hierholzer."""
        if len(self.grafo.edges()) == 0:
            return []
            
        grafo_temp = self.grafo.copy()
        vertice_atual = list(grafo_temp.nodes())[0]
        ciclo = [vertice_atual]
        
        while grafo_temp.number_of_edges() > 0:
            ciclo_parcial = self._encontrar_ciclo_parcial(grafo_temp, vertice_atual)
            indice = ciclo.index(vertice_atual)
            ciclo = ciclo[:indice] + ciclo_parcial + ciclo[indice+1:]
            
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
    
    def to_dict(self):
        """Converte o grafo para dicionário."""
        # Sincronizar arestas com o grafo NetworkX para garantir consistência
        arestas_sincronizadas = []
        for origem, destino in self.grafo.edges():
            arestas_sincronizadas.append((origem, destino))
        
        # Atualizar lista interna para manter sincronização
        self.arestas = arestas_sincronizadas
        
        return {
            "vertices": {nome: {"x": float(pos[0]), "y": float(pos[1])} 
                       for nome, pos in self.vertices.items()},
            "arestas": arestas_sincronizadas
        }
    
    def from_dict(self, dados):
        """Carrega o grafo de um dicionário."""
        self.grafo = nx.MultiGraph()
        self.vertices = {}
        self.arestas = []
        
        for nome, pos in dados.get("vertices", {}).items():
            self.adicionar_vertice(nome, pos["x"], pos["y"])
            
        for origem, destino in dados.get("arestas", []):
            self.adicionar_aresta(origem, destino)


# Instância global do grafo
grafo_atual = GrafoEuleriano()


@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')


@app.route('/api/grafo', methods=['GET'])
def get_grafo():
    """Retorna o estado atual do grafo."""
    return jsonify({
        "grafo": grafo_atual.to_dict(),
        "status": grafo_atual.verificar_euleriano()
    })


@app.route('/api/vertice', methods=['POST'])
def adicionar_vertice():
    """Adiciona um vértice ao grafo."""
    data = request.json
    nome = data.get('nome') or f"P{len(grafo_atual.vertices) + 1}"
    x = float(data.get('x'))
    y = float(data.get('y'))
    
    if nome in grafo_atual.vertices:
        return jsonify({"erro": f"Ponto '{nome}' já existe!"}), 400
        
    grafo_atual.adicionar_vertice(nome, x, y)
    return jsonify({
        "sucesso": True,
        "grafo": grafo_atual.to_dict(),
        "status": grafo_atual.verificar_euleriano()
    })


@app.route('/api/vertice/<nome>', methods=['DELETE'])
def remover_vertice(nome):
    """Remove um vértice do grafo."""
    if nome not in grafo_atual.vertices:
        return jsonify({"erro": f"Ponto '{nome}' não encontrado!"}), 404
        
    grafo_atual.remover_vertice(nome)
    return jsonify({
        "sucesso": True,
        "grafo": grafo_atual.to_dict(),
        "status": grafo_atual.verificar_euleriano()
    })


@app.route('/api/aresta', methods=['POST'])
def adicionar_aresta():
    """Adiciona uma aresta ao grafo."""
    data = request.json
    origem = data.get('origem')
    destino = data.get('destino')
    
    if origem not in grafo_atual.vertices or destino not in grafo_atual.vertices:
        return jsonify({"erro": "Pontos não encontrados!"}), 400
    
    # Verificar se a conexão já existe (evitar duplicatas desnecessárias)
    # Mas permitir múltiplas arestas entre os mesmos vértices se necessário
    grafo_atual.adicionar_aresta(origem, destino)
    
    return jsonify({
        "sucesso": True,
        "grafo": grafo_atual.to_dict(),
        "status": grafo_atual.verificar_euleriano()
    })


@app.route('/api/aresta', methods=['DELETE'])
def remover_aresta():
    """Remove uma aresta do grafo."""
    data = request.json
    origem = data.get('origem')
    destino = data.get('destino')
    
    grafo_atual.remover_aresta(origem, destino)
    return jsonify({
        "sucesso": True,
        "grafo": grafo_atual.to_dict(),
        "status": grafo_atual.verificar_euleriano()
    })


@app.route('/api/otimizar', methods=['POST'])
def otimizar():
    """Otimiza o caminho usando ciclo euleriano."""
    data = request.json
    velocidade = float(data.get('velocidade', 100.0))
    tempo_setup = float(data.get('tempo_setup', 0.5))
    
    euleriano, mensagem = grafo_atual.verificar_euleriano()
    
    if not euleriano:
        return jsonify({
            "erro": mensagem,
            "status": grafo_atual.verificar_euleriano()
        }), 400
        
    ciclo = grafo_atual.encontrar_ciclo_euleriano()
    
    if not ciclo:
        return jsonify({"erro": "Nenhum ciclo encontrado"}), 400
        
    distancia = grafo_atual.calcular_distancia_total(ciclo)
    tempo_corte = (distancia / velocidade) if velocidade > 0 else 0
    tempo_total = tempo_corte + tempo_setup
    
    # Gerar programa CNC
    programa_cnc = []
    programa_cnc.append(f"G00 X{grafo_atual.vertices[ciclo[0]][0]:.2f} Y{grafo_atual.vertices[ciclo[0]][1]:.2f}  ; Posicionamento inicial")
    programa_cnc.append(f"G01 F{velocidade:.1f}  ; Velocidade de corte")
    programa_cnc.append("")
    
    for i, ponto in enumerate(ciclo[1:], 1):
        x, y = grafo_atual.vertices[ponto]
        programa_cnc.append(f"N{i:03d} G01 X{x:.2f} Y{y:.2f}  ; Corte até ponto {ponto}")
    
    programa_cnc.append(f"\nG00 X{grafo_atual.vertices[ciclo[0]][0]:.2f} Y{grafo_atual.vertices[ciclo[0]][1]:.2f}  ; Retorno ao início")
    programa_cnc.append("M30  ; Fim do programa")
    
    return jsonify({
        "sucesso": True,
        "ciclo": ciclo,
        "distancia": distancia,
        "tempo_corte": tempo_corte,
        "tempo_setup": tempo_setup,
        "tempo_total": tempo_total,
        "programa_cnc": "\n".join(programa_cnc),
        "estatisticas": {
            "vertices_visitados": len(ciclo),
            "trajetorias_percorridas": len(ciclo) - 1
        }
    })


@app.route('/api/limpar', methods=['POST'])
def limpar():
    """Limpa o grafo atual."""
    global grafo_atual
    grafo_atual = GrafoEuleriano()
    return jsonify({
        "sucesso": True,
        "grafo": grafo_atual.to_dict()
    })


@app.route('/api/exemplo/<tipo>', methods=['POST'])
def exemplo(tipo):
    """Carrega um exemplo pré-definido."""
    global grafo_atual
    grafo_atual = GrafoEuleriano()
    
    import math
    
    # Coordenadas padrão do canvas (serão centralizadas no frontend)
    # Assumindo canvas médio de ~800x600, centro seria ~400x300
    centro_x = 400
    centro_y = 300
    
    if tipo == 'retangular':
        # Retângulo 50x30 centralizado
        largura = 50
        altura = 30
        grafo_atual.adicionar_vertice("P1", centro_x - largura/2, centro_y - altura/2)
        grafo_atual.adicionar_vertice("P2", centro_x + largura/2, centro_y - altura/2)
        grafo_atual.adicionar_vertice("P3", centro_x + largura/2, centro_y + altura/2)
        grafo_atual.adicionar_vertice("P4", centro_x - largura/2, centro_y + altura/2)
        grafo_atual.adicionar_aresta("P1", "P2")
        grafo_atual.adicionar_aresta("P2", "P3")
        grafo_atual.adicionar_aresta("P3", "P4")
        grafo_atual.adicionar_aresta("P4", "P1")
        
    elif tipo == 'estrela':
        raio_externo = 80
        raio_interno = 40
        
        pontos_externos = []
        for i in range(5):
            angulo = 2 * math.pi * i / 5 - math.pi/2
            x = centro_x + raio_externo * math.cos(angulo)
            y = centro_y + raio_externo * math.sin(angulo)
            nome = f"E{i+1}"
            grafo_atual.adicionar_vertice(nome, x, y)
            pontos_externos.append(nome)
            
        pontos_internos = []
        for i in range(5):
            angulo = 2 * math.pi * i / 5 - math.pi/2 + math.pi/5
            x = centro_x + raio_interno * math.cos(angulo)
            y = centro_y + raio_interno * math.sin(angulo)
            nome = f"I{i+1}"
            grafo_atual.adicionar_vertice(nome, x, y)
            pontos_internos.append(nome)
            
        for i in range(5):
            grafo_atual.adicionar_aresta(pontos_externos[i], pontos_internos[i])
            grafo_atual.adicionar_aresta(pontos_internos[i], pontos_externos[(i+1) % 5])
            
    elif tipo == 'grade':
        # Grade 3x3 centralizada
        espacamento = 60
        offset_x = centro_x - espacamento
        offset_y = centro_y - espacamento
        
        for i in range(3):
            for j in range(3):
                nome = f"P{i}{j}"
                x = offset_x + i * espacamento
                y = offset_y + j * espacamento
                grafo_atual.adicionar_vertice(nome, x, y)
                
        for i in range(3):
            for j in range(3):
                nome = f"P{i}{j}"
                if i < 2:
                    grafo_atual.adicionar_aresta(nome, f"P{i+1}{j}")
                if j < 2:
                    grafo_atual.adicionar_aresta(nome, f"P{i}{j+1}")
                    
        grafo_atual.adicionar_aresta("P00", "P22")
        grafo_atual.adicionar_aresta("P02", "P20")
    
    return jsonify({
        "sucesso": True,
        "grafo": grafo_atual.to_dict(),
        "status": grafo_atual.verificar_euleriano()
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

