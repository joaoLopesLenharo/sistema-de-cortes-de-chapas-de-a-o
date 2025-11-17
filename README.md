# ⚙️ Sistema de Otimização de Corte Contínuo (CNC/Laser)

Sistema completo para otimização de corte contínuo em máquinas CNC, corte laser ou usinagem, utilizando **Ciclos Eulerianos**. Disponível em duas versões: **Interface Web** (recomendada) e **Interface Desktop**.

## 📋 Índice

1. [Sobre o Projeto](#sobre-o-projeto)
2. [Conceito: Ciclos Eulerianos](#conceito-ciclos-eulerianos)
3. [Versões Disponíveis](#versões-disponíveis)
4. [Requisitos](#requisitos)
5. [Instalação](#instalação)
6. [Como Usar](#como-usar)
7. [Funcionalidades Detalhadas](#funcionalidades-detalhadas)
8. [Exemplos Práticos](#exemplos-práticos)
9. [Explicação Técnica](#explicação-técnica)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Sobre o Projeto

Este programa resolve o problema de **otimização de corte contínuo** em máquinas CNC, corte laser ou usinagem, utilizando o conceito matemático de **Ciclos Eulerianos**. 

O objetivo é encontrar o caminho mais eficiente para uma ferramenta de corte percorrer todas as trajetórias de uma peça **exatamente uma vez**, minimizando:
- ⏱️ Tempo de corte
- 🔄 Movimentos desnecessários
- ⚡ Consumo de energia
- 💰 Custo de produção

---

## 📚 Conceito: Ciclos Eulerianos

### O que é um Ciclo Euleriano?

Um **ciclo euleriano** é um caminho em um grafo que:
- ✅ Visita cada **aresta** (trajetória de corte) **exatamente uma vez**
- ✅ Retorna ao ponto inicial
- ✅ Não repete nenhuma trajetória

### Por que isso é importante para corte contínuo?

Em máquinas de corte contínuo (CNC, laser, usinagem), cada trajetória precisa ser cortada. Um ciclo euleriano garante que:

1. **Todas as trajetórias sejam cortadas** sem repetição
2. **A ferramenta não precise "levantar"** desnecessariamente
3. **O caminho seja otimizado** para mínimo tempo de corte

### Condições para Corte Contínuo

Para que um projeto possa ter corte contínuo otimizado, é necessário:

1. **Grafo Conexo**: Todos os pontos de corte devem estar conectados entre si
2. **Grau Par**: Cada ponto de corte deve ter um **número par** de trajetórias conectadas

> **Dica**: Se um ponto tiver número ímpar de trajetórias, adicione uma trajetória extra para torná-lo par.

---

## 🖥️ Versões Disponíveis

### 🌐 Versão Web (Recomendada)

**Arquivo**: `app.py`

**Características**:
- ✅ Interface web moderna e responsiva
- ✅ Canvas interativo com arrastar e soltar
- ✅ Animação de preenchimento progressivo das linhas
- ✅ Visualização em tempo real do caminho otimizado
- ✅ Funciona em qualquer navegador moderno
- ✅ Acessível de qualquer dispositivo na rede local

### 🖥️ Versão Desktop

**Arquivo**: `ciclo_euleriano_corte.py`

**Características**:
- ✅ Interface gráfica nativa (Tkinter)
- ✅ Visualização com Matplotlib
- ✅ Funciona offline
- ✅ Ideal para uso local sem servidor

---

## 📦 Requisitos

### Software Necessário

- **Python 3.7 ou superior**
- Bibliotecas Python (instaladas automaticamente via `requirements.txt`):
  - `flask` (versão web)
  - `flask-cors` (versão web)
  - `networkx` (manipulação de grafos)
  - `matplotlib` (versão desktop)
  - `tkinter` (versão desktop - geralmente já incluído no Python)

### Sistema Operacional

- ✅ Windows
- ✅ Linux
- ✅ macOS

### Navegador (Versão Web)

- ✅ Chrome/Edge (recomendado)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

---

## 🚀 Instalação

### Passo 1: Clone ou Baixe o Projeto

```bash
# Se usando Git
git clone <url-do-repositorio>
cd "Ciclos Eulerianos"

# Ou simplesmente baixe e extraia o arquivo ZIP
```

### Passo 2: Instale as Dependências

```bash
pip install -r requirements.txt
```

Isso instalará automaticamente:
- `flask` e `flask-cors` (para versão web)
- `networkx` (manipulação de grafos)
- `matplotlib` (para versão desktop)

### Passo 3: Execute o Programa

#### 🌐 Versão Web (Recomendada)

```bash
python app.py
```

Depois, abra seu navegador e acesse:
```
http://localhost:5000
```

A interface web será aberta automaticamente no navegador padrão.

#### 🖥️ Versão Desktop

```bash
python ciclo_euleriano_corte.py
```

A interface gráfica será aberta automaticamente.

---

## 🎮 Como Usar

### 🌐 Versão Web - Interface Principal

A interface web é dividida em **3 áreas principais**:

1. **🎛️ Painel de Controle** (esquerda)
   - Modos de operação (Definir Pontos / Definir Trajetórias)
   - Controles para adicionar pontos e trajetórias
   - Parâmetros da máquina (velocidade, tempo de setup)
   - Botões de ação (Otimizar, Animar, Limpar)
   - Exemplos pré-definidos

2. **🖥️ Canvas Interativo** (centro-direita)
   - Visualização da peça em tempo real
   - Clique para adicionar pontos
   - Arraste pontos para reposicionar
   - Visualização do caminho otimizado com animação
   - Números N1, N2, N3... mostrando ordem de corte

3. **📋 Painel de Resultados** (embaixo, quando otimizado)
   - Código G-code gerado
   - Estatísticas de produção
   - Distância total e tempo estimado

### 🖥️ Versão Desktop - Interface Principal

A interface desktop é dividida em **3 áreas principais**:

1. **🎛️ Painel de Controle da Máquina** (esquerda)
   - Controles e configurações
   - Parâmetros da máquina
   - Status do projeto

2. **🖥️ Mesa de Trabalho** (centro-direita)
   - Visualização da peça
   - Definição de pontos e trajetórias
   - Visualização do caminho otimizado

3. **📋 Programa CNC** (embaixo)
   - Código G-code gerado
   - Estatísticas de produção

---

## 📖 Funcionalidades Detalhadas

### 1. 🔧 Modo de Operação

#### 📍 Modo: Definir Pontos de Corte

**O que faz**: Permite adicionar pontos de corte na peça.

**Como usar**:
- **Método 1**: Clique diretamente na mesa de trabalho onde deseja o ponto
- **Método 2**: Use os campos de entrada:
  - **ID Ponto**: Nome identificador (ex: P1, P2, ou deixe em branco para auto-numeração)
  - **X (mm)**: Coordenada X em milímetros
  - **Y (mm)**: Coordenada Y em milímetros
  - Clique em **"📍 Adicionar Ponto"** ou pressione **Enter**

**Dica**: Você pode pressionar **Enter** em qualquer campo para confirmar.

#### ✂️ Modo: Definir Trajetórias de Corte

**O que faz**: Conecta pontos de corte para criar trajetórias que serão cortadas.

**Como usar** (Versão Web):
- **Método 1**: 
  1. Selecione o modo **"✂️ Definir Trajetórias"**
  2. Clique no primeiro ponto de corte (ficará vermelho)
  3. Mova o mouse - uma linha azul temporária aparecerá
  4. Clique no segundo ponto de corte
  5. A trajetória será criada automaticamente
- **Método 2**: Use os campos de entrada:
  - **Ponto 1**: Selecione o primeiro ponto
  - **Ponto 2**: Selecione o segundo ponto
  - Clique em **"🔗 Conectar"**

**Como usar** (Versão Desktop):
- **Método 1**: 
  1. Clique no primeiro ponto de corte
  2. Clique no segundo ponto de corte
  3. A trajetória será criada automaticamente
- **Método 2**: Use os campos de entrada:
  - **Ponto Inicial**: ID do primeiro ponto
  - **Ponto Final**: ID do segundo ponto
  - Clique em **"✂️ Adicionar Trajetória"** ou pressione **Enter**

**Importante**: 
- Cada trajetória representa um corte que será feito
- Para corte contínuo, cada ponto deve ter número **par** de trajetórias
- **Versão Web**: Você pode arrastar pontos e as conexões são mantidas automaticamente

---

### 2. ⚙️ Parâmetros da Máquina

#### Velocidade de Corte (mm/min)

**O que é**: Velocidade com que a ferramenta se move durante o corte.

**Valores típicos**:
- Corte laser: 100-500 mm/min
- CNC madeira: 200-1000 mm/min
- CNC metal: 50-300 mm/min

**Como alterar**: Digite o valor e pressione **Enter**

#### Tempo de Setup (min)

**O que é**: Tempo necessário para preparar a máquina antes do corte (posicionamento, fixação, etc.).

**Valores típicos**: 0.5 - 2.0 minutos

**Como alterar**: Digite o valor e pressione **Enter**

---

### 3. 🎯 Operações da Máquina

#### 🚀 Otimizar Caminho da Ferramenta

**O que faz**: 
- Verifica se o projeto permite corte contínuo
- Encontra o caminho otimizado usando algoritmo de Hierholzer
- Gera o programa CNC (G-code)
- Calcula tempo e distância estimados

**Quando usar**: Após definir todos os pontos e trajetórias.

**Resultado**:
- Caminho otimizado destacado em **vermelho** na mesa de trabalho
- Programa CNC gerado na área de resultados
- Estatísticas de produção atualizadas
- **Versão Web**: Botão "▶️ Animar Corte" aparece para visualizar a sequência

**Possíveis erros**:
- ⚠️ **Grafo não conexo**: Adicione trajetórias para conectar todos os pontos
- ⚠️ **Vértices com grau ímpar**: Adicione trajetórias extras para tornar todos os pontos pares

#### ▶️ Animar Corte (Versão Web)

**O que faz**: 
- Mostra visualmente a ordem de corte das trajetórias
- Anima o preenchimento progressivo de cada linha em vermelho
- Cada linha é preenchida gradualmente em 600ms
- Números N1, N2, N3... aparecem conforme as linhas são preenchidas

**Como usar**:
1. Otimize o caminho primeiro
2. Clique em **"▶️ Animar Corte"**
3. Observe as linhas sendo preenchidas sequencialmente
4. Use **"⏹️ Parar Animação"** para interromper a qualquer momento

**Características**:
- Animação suave usando `requestAnimationFrame`
- Múltiplas linhas podem estar preenchendo simultaneamente
- Para automaticamente quando todas as linhas estão completas

#### 🗑️ Limpar Projeto

**O que faz**: Remove todos os pontos e trajetórias, iniciando um novo projeto.

**Atenção**: Esta ação não pode ser desfeita!

#### 🗑️ Excluir Ponto (Versão Web)

**O que faz**: Remove um ponto específico e suas trajetórias associadas.

**Como usar**:
- **Método 1**: Clique com botão direito em um ponto
- **Método 2**: Selecione um ponto e pressione **Delete** ou **Backspace**
- **Método 3**: Selecione um ponto e clique no botão **"🗑️ Excluir Ponto Selecionado"**

**Nota**: As trajetórias conectadas ao ponto são removidas automaticamente.

#### ➖ Remover Último Ponto (Versão Desktop)

**O que faz**: Remove o último ponto de corte adicionado (e suas trajetórias associadas).

---

### 4. 📦 Peças Pré-definidas

Exemplos rápidos para testar o sistema:

#### ⬜ Placa Retangular
- 4 pontos formando um retângulo
- Perímetro completo para corte
- Ideal para testar conceitos básicos

#### ⭐ Peça em Estrela
- 10 pontos (5 externos + 5 internos)
- Formato de estrela de 5 pontas
- Exemplo de peça complexa

#### 🔷 Grade com Furos
- 9 pontos em grade 3x3
- Padrão de corte em grade
- Exemplo de estrutura regular

**Como usar**: Clique em qualquer botão para carregar o exemplo.

---

### 5. 💾 Arquivo

#### 💾 Salvar Grafo

**O que faz**: Salva o projeto atual em arquivo JSON.

**Formato**: JSON com pontos e trajetórias

**Uso**: 
- Salve projetos para reutilização
- Compartilhe configurações
- Mantenha histórico de projetos

#### 📂 Carregar Grafo

**O que faz**: Carrega um projeto salvo anteriormente.

**Uso**: 
- Retome trabalhos anteriores
- Use projetos de outros usuários
- Teste diferentes configurações

---

### 6. 📊 Status do Projeto

Exibe informações em tempo real:

- **Pontos de Corte**: Quantidade de pontos definidos
- **Trajetórias**: Quantidade de trajetórias definidas
- **Status**: Se o projeto está pronto para otimização
- **Trajetórias por Ponto**: Lista mostrando quantas trajetórias cada ponto possui
  - ✓ = número par (ok para corte contínuo)
  - ✗ = número ímpar (precisa ajuste)

**⏱️ Tempo Estimado** (quando otimizado):
- Tempo de corte
- Tempo total (incluindo setup)
- Distância total percorrida

---

### 7. 💡 Instruções Contextuais

Painel que mostra instruções baseadas no modo atual:

- **Modo Ponto**: Como adicionar pontos
- **Modo Trajetória**: Como conectar pontos
- **Ponto Selecionado**: Próximos passos

---

## 🎨 Visualização na Mesa de Trabalho

### Elementos Visuais

#### Pontos de Corte
- **Azul** (#2563eb): Pontos normais
- **Vermelho** (#ef4444): Ponto selecionado (Versão Web)
- **Verde** (#10b981): Ponto inicial do ciclo otimizado

#### Trajetórias
- **Cinza tracejado**: Trajetórias definidas (ainda não otimizadas)
- **Vermelho sólido**: Caminho otimizado da ferramenta
- **Vermelho mais grosso (5px)**: Durante animação (Versão Web)
- **Números (N1, N2, ...)**: Ordem das etapas no programa CNC
  - **Versão Web**: Números aparecem em círculos brancos com borda preta
  - Aparecem quando a linha está 50% preenchida durante animação

#### Feedback Visual (Versão Web)
- **Linha azul temporária**: Aparece ao selecionar um ponto no modo trajetória
- **Círculo azul**: Indica ponto próximo ao mouse para conexão
- **Animação de preenchimento**: Linhas preenchem progressivamente de 0% a 100%

### Interações

#### Versão Web
- **Clique**: Adiciona ponto ou seleciona ponto (dependendo do modo)
- **Arrastar**: Move pontos mantendo conexões
- **Clique direito**: Exclui ponto
- **Delete/Backspace**: Exclui ponto selecionado
- **Hover**: Mostra feedback visual de pontos próximos
- **Zoom automático**: Canvas ajusta automaticamente para mostrar todos os pontos

#### Versão Desktop
- **Hover**: Ao passar o mouse sobre a mesa, o título mostra o ponto mais próximo
- **Clique**: Adiciona ponto ou seleciona ponto (dependendo do modo)
- **Zoom automático**: A visualização ajusta automaticamente para mostrar todos os pontos

---

## 📋 Programa CNC Gerado

### Formato G-code

O programa gerado segue o padrão G-code usado em máquinas CNC:

```
G00 X0.00 Y0.00  ; Posicionamento inicial (movimento rápido)
G01 F100.0       ; Velocidade de corte

N001 G01 X50.00 Y0.00  ; Corte até ponto P2
N002 G01 X50.00 Y30.00 ; Corte até ponto P3
N003 G01 X0.00 Y30.00  ; Corte até ponto P4
N004 G01 X0.00 Y0.00   ; Corte até ponto P1

G00 X0.00 Y0.00  ; Retorno ao início (movimento rápido)
M30              ; Fim do programa
```

### Comandos Explicados

- **G00**: Movimento rápido (sem corte) - usado para posicionamento
- **G01**: Movimento linear com corte - usado durante o corte
- **F**: Define velocidade de avanço (mm/min)
- **X, Y**: Coordenadas em milímetros
- **N###**: Número da linha (opcional, para referência)
- **M30**: Fim do programa

### Estatísticas de Produção

Após otimização, são exibidas:
- **Distância total percorrida**: Soma de todas as trajetórias (mm)
- **Tempo de corte**: Calculado com base na velocidade (min)
- **Tempo de setup**: Tempo de preparação (min)
- **Tempo total estimado**: Soma de corte + setup (min)
- **Trajetórias percorridas**: Quantidade de cortes realizados

---

## 🔬 Explicação Técnica

### Algoritmo de Hierholzer

O programa utiliza o **algoritmo de Hierholzer** para encontrar o ciclo euleriano:

1. **Escolhe um vértice inicial** (ponto de corte)
2. **Encontra um ciclo** a partir desse vértice
3. **Repete** até que todas as arestas sejam visitadas
4. **Combina** os ciclos parciais em um ciclo completo

### Estrutura de Dados

- **Grafo**: Representado usando `networkx.MultiGraph`
- **Vértices**: Pontos de corte com coordenadas (x, y)
- **Arestas**: Trajetórias de corte entre pontos

### Verificação Euleriana

Antes de otimizar, o sistema verifica:

1. **Conectividade**: Usa `nx.is_connected()` para verificar se todos os pontos estão conectados
2. **Grau Par**: Verifica se cada vértice tem grau par usando `grafo.degree(v) % 2 == 0`

---

## 🎓 Exemplos Práticos

### Exemplo 1: Corte de Perímetro Retangular

**Objetivo**: Cortar o perímetro de uma placa retangular de 50mm x 30mm.

**Passos**:
1. Selecione modo **"📍 Definir Pontos de Corte"**
2. Adicione 4 pontos:
   - P1: (0, 0)
   - P2: (50, 0)
   - P3: (50, 30)
   - P4: (0, 30)
3. Selecione modo **"✂️ Definir Trajetórias de Corte"**
4. Conecte: P1→P2, P2→P3, P3→P4, P4→P1
5. Clique em **"🚀 Otimizar Caminho da Ferramenta"**

**Resultado**: Caminho que percorre todo o perímetro sem repetir trajetórias.

### Exemplo 2: Peça com Padrão Complexo

**Objetivo**: Criar uma peça com múltiplos caminhos interconectados.

**Passos**:
1. Defina pontos de corte formando o padrão desejado
2. Conecte os pontos criando todas as trajetórias necessárias
3. **Importante**: Certifique-se de que cada ponto tenha número par de conexões
4. Se algum ponto tiver número ímpar, adicione uma trajetória extra
5. Otimize o caminho

**Dica**: Use o painel "📊 Status do Projeto" para verificar a paridade de cada ponto.

---

## ❓ Troubleshooting

### Problema: "Grafo não é conexo"

**Causa**: Existem pontos isolados ou grupos desconectados.

**Solução**: 
- Adicione trajetórias para conectar todos os pontos
- Verifique se não há pontos "órfãos" sem conexões

### Problema: "Vértices com grau ímpar"

**Causa**: Algum ponto tem número ímpar de trajetórias.

**Solução**:
- Identifique os pontos com grau ímpar (marcados com ✗ no status)
- Adicione trajetórias extras para tornar todos os pontos pares
- Dica: Você pode adicionar trajetórias duplicadas se necessário

### Problema: "Nenhum ciclo encontrado"

**Causa**: Não há trajetórias definidas ou o grafo está vazio.

**Solução**:
- Certifique-se de ter pelo menos 2 pontos
- Adicione pelo menos uma trajetória entre pontos

### Problema: Interface não abre

**Causa**: Dependências não instaladas ou Python incorreto.

**Solução**:
```bash
# Verifique a versão do Python
python --version  # Deve ser 3.7 ou superior

# Reinstale as dependências
pip install --upgrade matplotlib networkx
```

### Problema: Erro ao salvar/carregar

**Causa**: Permissões de arquivo ou formato JSON inválido.

**Solução**:
- Verifique permissões da pasta
- Não edite manualmente arquivos JSON salvos
- Use apenas a função de carregar do programa

---

## 📝 Notas Importantes

### Limitações

- O algoritmo assume que todas as trajetórias têm o mesmo peso (distância)
- Não considera aceleração/desaceleração da máquina
- Tempo de setup é fixo (não varia com complexidade)

### Boas Práticas

1. **Planeje antes de definir pontos**: Tenha um esboço mental da peça
2. **Verifique paridade**: Sempre verifique se todos os pontos têm grau par antes de otimizar
3. **Use exemplos**: Comece com os exemplos pré-definidos para entender o funcionamento
4. **Salve frequentemente**: Salve projetos importantes para não perder trabalho
5. **Ajuste velocidade**: Configure velocidade de corte realista para sua máquina

### Dicas de Otimização

- **Minimize pontos**: Use apenas pontos necessários
- **Evite cruzamentos**: Trajetórias que se cruzam podem ser reorganizadas
- **Considere material**: Velocidade de corte varia com material e espessura
- **Teste primeiro**: Sempre teste em material de baixo valor primeiro

---

## 🔗 Referências

### Conceitos Matemáticos

- **Teoria dos Grafos**: Estudo de estruturas que modelam relações entre objetos
- **Ciclo Euleriano**: Conceito introduzido por Leonhard Euler em 1736
- **Algoritmo de Hierholzer**: Método eficiente para encontrar ciclos eulerianos

### Aplicações Práticas

- **CNC**: Controle Numérico Computadorizado
- **Corte Laser**: Processo de corte usando laser
- **Usinagem**: Processo de remoção de material

---

## 📄 Licença

Este projeto é fornecido como está, para fins educacionais e de demonstração.

---

## 👨‍💻 Autor

Desenvolvido para demonstrar a aplicação prática de Ciclos Eulerianos em problemas de otimização de corte contínuo.

---

## 🆘 Suporte

Para dúvidas ou problemas:
1. Consulte esta documentação
2. Verifique a seção Troubleshooting
3. Revise os exemplos práticos
4. Teste com os exemplos pré-definidos

---

## 📁 Estrutura do Projeto

```
Ciclos Eulerianos/
│
├── app.py                      # Aplicação Flask (versão web)
├── ciclo_euleriano_corte.py    # Aplicação desktop (Tkinter)
├── requirements.txt             # Dependências Python
├── README.md                    # Este arquivo
├── apresentacao.md             # Roteiro de apresentação
│
├── templates/
│   └── index.html              # Interface HTML (versão web)
│
└── static/
    ├── app.js                  # Lógica JavaScript (versão web)
    └── style.css               # Estilos CSS (versão web)
```

## 🔄 Diferenças entre Versões

| Característica | Versão Web | Versão Desktop |
|---------------|------------|----------------|
| Interface | HTML/CSS/JavaScript | Tkinter |
| Visualização | Canvas HTML5 | Matplotlib |
| Animação | ✅ Preenchimento progressivo | ❌ |
| Arrastar pontos | ✅ | ❌ |
| Excluir pontos | ✅ Múltiplos métodos | ❌ |
| Acesso remoto | ✅ Via rede local | ❌ |
| Requer servidor | ✅ Flask | ❌ |

## 🆕 Novidades da Versão Web

- ✨ **Animação de preenchimento progressivo**: Visualize como cada trajetória é cortada
- 🎯 **Canvas interativo**: Arraste pontos mantendo conexões
- 🗑️ **Exclusão intuitiva**: Clique direito ou Delete para remover pontos
- 📱 **Interface responsiva**: Funciona bem em diferentes tamanhos de tela
- 🎨 **Visual moderno**: Design limpo e intuitivo
- ⚡ **Feedback visual**: Linhas temporárias e highlights ao criar conexões

---

**Versão**: 2.0  
**Última atualização**: 2024
