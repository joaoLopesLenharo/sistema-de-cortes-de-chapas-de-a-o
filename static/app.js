// Estado da aplicação
let state = {
    mode: 'point', // 'point' ou 'edge'
    points: {},
    edges: [],
    selectedPoint: null,
    optimizedPath: null,
    canvas: null,
    ctx: null,
    scale: 1,
    offsetX: 0,
    offsetY: 0,
    isDragging: false,
    dragPoint: null,
    lastMousePos: null,
    animationStep: 0, // Etapa atual da animação
    animationInterval: null, // Intervalo da animação
    isAnimating: false, // Se está animando
    lineProgress: {}, // Progresso de preenchimento de cada linha (0-1)
    animationFrame: null // ID do requestAnimationFrame
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    initCanvas();
    initEventListeners();
    carregarGrafo();
});

function initCanvas() {
    state.canvas = document.getElementById('canvas');
    state.ctx = state.canvas.getContext('2d');
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Eventos do canvas
    state.canvas.addEventListener('click', handleCanvasClick);
    state.canvas.addEventListener('contextmenu', handleRightClick);
    state.canvas.addEventListener('mousemove', handleCanvasMove);
    state.canvas.addEventListener('mousedown', handleCanvasMouseDown);
    state.canvas.addEventListener('mouseup', handleCanvasMouseUp);
    state.canvas.addEventListener('mouseleave', handleCanvasMouseUp);
    
    // Evento de teclado para Delete
    document.addEventListener('keydown', handleKeyDown);
}

function resizeCanvas() {
    const container = state.canvas.parentElement;
    state.canvas.width = container.clientWidth;
    state.canvas.height = container.clientHeight;
    draw();
}

function initEventListeners() {
    // Modo de operação
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.mode = btn.dataset.mode;
            state.selectedPoint = null;
            updateModeIndicator();
            draw();
        });
    });
    
    // Enter nos campos
    ['point-id', 'point-x', 'point-y'].forEach(id => {
        document.getElementById(id).addEventListener('keypress', (e) => {
            if (e.key === 'Enter') adicionarPontoManual();
        });
    });
}

function updateModeIndicator() {
    const text = state.mode === 'point' ? 'Definir Pontos' : 'Definir Trajetórias';
    document.getElementById('mode-text').textContent = `Modo: ${text}`;
    atualizarHint();
}

// API Calls
async function carregarGrafo() {
    try {
        const response = await fetch('/api/grafo');
        const data = await response.json();
        console.log('Dados recebidos do servidor:', data);
        
        state.points = data.grafo.vertices || {};
        state.edges = data.grafo.arestas || [];
        
        console.log('Estado atualizado - Pontos:', Object.keys(state.points).length, 'Arestas:', state.edges.length);
        console.log('Pontos:', state.points);
        console.log('Arestas:', state.edges);
        
        atualizarSelects();
        atualizarStatus();
        atualizarHint();
        draw();
    } catch (error) {
        console.error('Erro ao carregar grafo:', error);
    }
}

async function adicionarPonto(x, y, nome = null) {
    if (!nome) {
        nome = `P${Object.keys(state.points).length + 1}`;
    }
    
    try {
        const response = await fetch('/api/vertice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, x, y })
        });
        
        if (!response.ok) {
            const error = await response.json();
            alert(error.erro || 'Erro ao adicionar ponto');
            return;
        }
        
        const data = await response.json();
        state.points = data.grafo.vertices;
        state.edges = data.grafo.arestas;
        atualizarSelects();
        atualizarStatus(data.status);
        atualizarHint();
        draw();
    } catch (error) {
        console.error('Erro ao adicionar ponto:', error);
    }
}

async function adicionarPontoManual() {
    const id = document.getElementById('point-id').value.trim();
    const x = parseFloat(document.getElementById('point-x').value);
    const y = parseFloat(document.getElementById('point-y').value);
    
    if (isNaN(x) || isNaN(y)) {
        alert('Informe coordenadas válidas!');
        return;
    }
    
    await adicionarPonto(x, y, id || null);
    
    // Limpar campos
    document.getElementById('point-id').value = '';
    document.getElementById('point-x').value = '';
    document.getElementById('point-y').value = '';
    
    // Hint já é atualizado em adicionarPonto()
}

async function adicionarTrajetoria() {
    const from = document.getElementById('edge-from').value;
    const to = document.getElementById('edge-to').value;
    
    if (!from || !to) {
        alert('Selecione dois pontos!');
        return;
    }
    
    if (from === to) {
        alert('Selecione pontos diferentes!');
        return;
    }
    
    try {
        const response = await fetch('/api/aresta', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ origem: from, destino: to })
        });
        
        if (!response.ok) {
            const error = await response.json();
            alert(error.erro || 'Erro ao adicionar trajetória');
            return;
        }
        
        const data = await response.json();
        state.points = data.grafo.vertices;
        state.edges = data.grafo.arestas;
        atualizarSelects();
        atualizarStatus(data.status);
        atualizarHint();
        draw();
    } catch (error) {
        console.error('Erro ao adicionar trajetória:', error);
    }
}

async function otimizar() {
    const velocidade = parseFloat(document.getElementById('velocidade').value) || 100;
    const tempoSetup = parseFloat(document.getElementById('tempo-setup').value) || 0.5;
    
    try {
        const response = await fetch('/api/otimizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ velocidade, tempo_setup: tempoSetup })
        });
        
        if (!response.ok) {
            const error = await response.json();
            alert(`Erro: ${error.erro || 'Não foi possível otimizar'}`);
            return;
        }
        
        const data = await response.json();
        state.optimizedPath = data.ciclo;
        state.animationStep = 0; // Resetar animação
        state.lineProgress = {}; // Resetar progresso das linhas
        pararAnimacao(); // Parar qualquer animação anterior
        mostrarResultados(data);
        
        // Mostrar botão de animar
        const btnAnimar = document.getElementById('btn-animar');
        if (btnAnimar) {
            btnAnimar.style.display = 'block';
        }
        
        draw();
    } catch (error) {
        console.error('Erro ao otimizar:', error);
    }
}

function animarCaminho() {
    if (!state.optimizedPath || state.optimizedPath.length < 2) {
        alert('Nenhum caminho otimizado encontrado. Otimize primeiro!');
        return;
    }
    
    // Se já está animando, não fazer nada
    if (state.isAnimating) {
        return;
    }
    
    // Resetar para o início
    state.animationStep = 0;
    state.lineProgress = {};
    state.isAnimating = true;
    
    // Mostrar/esconder botões
    const btnAnimar = document.getElementById('btn-animar');
    const btnParar = document.getElementById('btn-parar-animacao');
    if (btnAnimar) btnAnimar.style.display = 'none';
    if (btnParar) btnParar.style.display = 'block';
    
    // Duração da animação de preenchimento de cada linha (600ms)
    const animationDuration = 600;
    
    // Iniciar loop de animação com requestAnimationFrame
    function animate() {
        if (!state.isAnimating) return;
        
        // Atualizar progresso de todas as linhas ativas
        const currentTime = Date.now();
        
        for (let i = 0; i < state.animationStep; i++) {
            if (!state.lineProgress[i]) {
                state.lineProgress[i] = { startTime: currentTime, progress: 0 };
            }
            
            const elapsed = currentTime - state.lineProgress[i].startTime;
            state.lineProgress[i].progress = Math.min(elapsed / animationDuration, 1);
        }
        
        draw();
        
        // Continuar animação se ainda há linhas para animar ou linhas sendo preenchidas
        const hasActiveAnimations = Object.values(state.lineProgress).some(p => p.progress < 1);
        if (state.animationStep < state.optimizedPath.length - 1 || hasActiveAnimations) {
            state.animationFrame = requestAnimationFrame(animate);
        } else {
            // Todas as animações terminaram
            pararAnimacao();
        }
    }
    
    // Iniciar animação: incrementar step a cada 800ms
    state.animationInterval = setInterval(() => {
        if (state.animationStep < state.optimizedPath.length - 1) {
            state.animationStep++;
            // Iniciar progresso da nova linha
            state.lineProgress[state.animationStep - 1] = {
                startTime: Date.now(),
                progress: 0
            };
        } else {
            // Todas as linhas foram iniciadas, parar intervalo
            clearInterval(state.animationInterval);
            state.animationInterval = null;
        }
    }, 800);
    
    // Iniciar loop de animação
    state.animationFrame = requestAnimationFrame(animate);
    
    // Desenhar primeiro frame
    draw();
}

function pararAnimacao() {
    if (state.animationInterval) {
        clearInterval(state.animationInterval);
        state.animationInterval = null;
    }
    
    if (state.animationFrame) {
        cancelAnimationFrame(state.animationFrame);
        state.animationFrame = null;
    }
    
    state.isAnimating = false;
    
    // Completar progresso de todas as linhas iniciadas
    Object.keys(state.lineProgress).forEach(key => {
        state.lineProgress[key].progress = 1;
    });
    
    // Mostrar/esconder botões
    const btnAnimar = document.getElementById('btn-animar');
    const btnParar = document.getElementById('btn-parar-animacao');
    if (btnAnimar && state.optimizedPath) {
        btnAnimar.style.display = 'block';
    }
    if (btnParar) btnParar.style.display = 'none';
    
    // Se parou no meio, mostrar todas as linhas
    if (state.animationStep > 0 && state.animationStep < (state.optimizedPath?.length - 1 || 0)) {
        state.animationStep = state.optimizedPath.length - 1;
    }
    
    draw();
}

async function limparProjeto() {
    if (!confirm('Deseja realmente limpar todo o projeto?')) return;
    
    try {
        pararAnimacao(); // Parar animação se estiver rodando
        await fetch('/api/limpar', { method: 'POST' });
        state.points = {};
        state.edges = [];
        state.selectedPoint = null;
        state.optimizedPath = null;
        state.animationStep = 0;
        atualizarSelects();
        atualizarStatus();
        atualizarHint();
        fecharResultados();
        
        // Esconder botões de animação
        const btnAnimar = document.getElementById('btn-animar');
        const btnParar = document.getElementById('btn-parar-animacao');
        if (btnAnimar) btnAnimar.style.display = 'none';
        if (btnParar) btnParar.style.display = 'none';
        
        draw();
    } catch (error) {
        console.error('Erro ao limpar:', error);
    }
}

async function carregarExemplo(tipo) {
    try {
        const response = await fetch(`/api/exemplo/${tipo}`, { method: 'POST' });
        const data = await response.json();
        
        // Calcular centro do canvas atual
        const centroX = state.canvas.width / 2;
        const centroY = state.canvas.height / 2;
        
        // Calcular offset para centralizar os pontos
        // Os exemplos são criados com centro em (400, 300)
        const offsetX = centroX - 400;
        const offsetY = centroY - 300;
        
        // Ajustar todas as coordenadas dos pontos
        const pontosAjustados = {};
        Object.entries(data.grafo.vertices).forEach(([nome, pos]) => {
            pontosAjustados[nome] = {
                x: pos.x + offsetX,
                y: pos.y + offsetY
            };
        });
        
        // Atualizar pontos ajustados no servidor
        // Limpar primeiro
        await fetch('/api/limpar', { method: 'POST' });
        
        // Adicionar pontos ajustados
        for (const [nome, pos] of Object.entries(pontosAjustados)) {
            await fetch('/api/vertice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nome, x: pos.x, y: pos.y })
            });
        }
        
        // Adicionar arestas
        for (const [origem, destino] of data.grafo.arestas) {
            await fetch('/api/aresta', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ origem, destino })
            });
        }
        
        // Recarregar grafo atualizado
        await carregarGrafo();
        state.selectedPoint = null;
        state.optimizedPath = null;
        fecharResultados();
    } catch (error) {
        console.error('Erro ao carregar exemplo:', error);
    }
}

// Canvas Handlers
function handleCanvasClick(e) {
    // Não processar clique se estiver arrastando
    if (state.isDragging) {
        state.isDragging = false;
        state.dragPoint = null;
        return;
    }
    
    const rect = state.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    console.log(`Clique no canvas - Modo: ${state.mode}, X: ${x}, Y: ${y}`);
    
    if (state.mode === 'point') {
        adicionarPonto(x, y);
    } else if (state.mode === 'edge') {
        const clickedPoint = encontrarPontoProximo(x, y);
        console.log(`Ponto próximo encontrado: ${clickedPoint}`);
        
        if (clickedPoint) {
            if (!state.selectedPoint) {
                // Primeiro clique: seleciona o ponto
                console.log(`Selecionando ponto: ${clickedPoint}`);
                state.selectedPoint = clickedPoint;
                atualizarHint();
                draw();
            } else if (state.selectedPoint !== clickedPoint) {
                // Segundo clique em ponto diferente: conecta
                console.log(`Conectando ${state.selectedPoint} -> ${clickedPoint}`);
                conectarPontos(state.selectedPoint, clickedPoint);
                state.selectedPoint = null;
                atualizarHint();
            } else {
                // Clicou no mesmo ponto: deseleciona
                console.log('Deselecionando ponto');
                state.selectedPoint = null;
                atualizarHint();
                draw();
            }
        } else {
            // Clicou fora de qualquer ponto: deseleciona
            if (state.selectedPoint) {
                console.log('Clicou fora, deselecionando');
                state.selectedPoint = null;
                atualizarHint();
                draw();
            }
        }
    }
}

function handleRightClick(e) {
    e.preventDefault(); // Prevenir menu de contexto
    
    const rect = state.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const clickedPoint = encontrarPontoProximo(x, y);
    if (clickedPoint) {
        excluirPonto(clickedPoint);
    }
}

function handleKeyDown(e) {
    // Tecla Delete ou Backspace para excluir ponto selecionado
    if ((e.key === 'Delete' || e.key === 'Backspace') && state.selectedPoint) {
        e.preventDefault();
        excluirPonto(state.selectedPoint);
    }
}

function handleCanvasMove(e) {
    const rect = state.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Salvar posição do mouse para linha temporária
    state.lastMousePos = { x, y };
    
    if (state.isDragging && state.dragPoint) {
        const point = state.points[state.dragPoint];
        point.x = x;
        point.y = y;
        draw();
    } else {
        const point = encontrarPontoProximo(x, y);
        if (state.mode === 'edge') {
            state.canvas.style.cursor = point ? 'pointer' : 'not-allowed';
        } else {
            state.canvas.style.cursor = point ? 'move' : 'crosshair';
        }
        // Redesenhar para mostrar linha temporária se houver ponto selecionado
        if (state.selectedPoint && state.mode === 'edge') {
            draw();
        }
    }
}

function handleCanvasMouseDown(e) {
    // Não iniciar arrasto se estiver no modo edge (deixa o clique processar)
    if (state.mode === 'edge') {
        return;
    }
    
    const rect = state.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const point = encontrarPontoProximo(x, y);
    if (point && state.mode === 'point') {
        state.isDragging = true;
        state.dragPoint = point;
    }
}

function handleCanvasMouseUp() {
    if (state.isDragging && state.dragPoint) {
        // Atualizar ponto no servidor
        const point = state.points[state.dragPoint];
        atualizarPontoNoServidor(state.dragPoint, point.x, point.y);
    }
    state.isDragging = false;
    state.dragPoint = null;
}

async function atualizarPontoNoServidor(nome, x, y) {
    // Salvar TODAS as conexões antes de atualizar
    const todasConexoes = [...state.edges];
    
    // Atualizar posição do ponto localmente para feedback visual
    if (state.points[nome]) {
        state.points[nome].x = x;
        state.points[nome].y = y;
    }
    
    // Atualizar no servidor - remover e readicionar mantendo conexões
    try {
        // Passo 1: Remover ponto (isso remove automaticamente todas as conexões dele)
        await fetch(`/api/vertice/${nome}`, { method: 'DELETE' });
        
        // Passo 2: Readicionar ponto na nova posição
        await fetch('/api/vertice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, x, y })
        });
        
        // Passo 3: Restaurar TODAS as conexões uma por uma
        // Usar Promise.all para fazer todas as requisições em paralelo (mais rápido)
        const promessas = todasConexoes.map(([origem, destino]) => 
            fetch('/api/aresta', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ origem, destino })
            })
        );
        
        await Promise.all(promessas);
        
        // Passo 4: Recarregar estado completo do servidor para garantir sincronização
        await carregarGrafo();
    } catch (error) {
        console.error('Erro ao atualizar ponto:', error);
        // Recarregar em caso de erro para restaurar estado consistente
        await carregarGrafo();
    }
}

function encontrarPontoProximo(x, y, limite = 30) {
    let menorDistancia = Infinity;
    let pontoProximo = null;
    
    for (const [nome, pos] of Object.entries(state.points)) {
        const distancia = Math.sqrt((x - pos.x)**2 + (y - pos.y)**2);
        if (distancia < menorDistancia && distancia < limite) {
            menorDistancia = distancia;
            pontoProximo = nome;
        }
    }
    
    return pontoProximo;
}

async function conectarPontos(from, to) {
    try {
        console.log(`Conectando pontos: ${from} -> ${to}`);
        
        const response = await fetch('/api/aresta', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ origem: from, destino: to })
        });
        
        if (!response.ok) {
            const error = await response.json();
            alert(error.erro || 'Erro ao conectar pontos');
            return;
        }
        
        const data = await response.json();
        console.log('Resposta do servidor:', data);
        
        // Atualizar estado local com dados do servidor
        state.points = data.grafo.vertices;
        state.edges = data.grafo.arestas;
        
        console.log('Estado atualizado - Pontos:', Object.keys(state.points).length, 'Arestas:', state.edges.length);
        console.log('Arestas:', state.edges);
        
        // Verificar se a conexão foi realmente adicionada
        // Suportar diferentes formatos de arestas
        const conexaoExiste = state.edges.some((edge) => {
            let origem, destino;
            if (Array.isArray(edge)) {
                [origem, destino] = edge;
            } else if (edge.origem && edge.destino) {
                origem = edge.origem;
                destino = edge.destino;
            } else {
                return false;
            }
            return (origem === from && destino === to) || (origem === to && destino === from);
        });
        
        if (!conexaoExiste) {
            console.warn('Conexão não foi adicionada corretamente, recarregando...');
            await carregarGrafo();
            return;
        }
        
        atualizarSelects();
        atualizarStatus(data.status);
        atualizarHint();
        draw();
        
        console.log('Trajetória criada com sucesso!');
        console.log('Total de arestas agora:', state.edges.length);
    } catch (error) {
        console.error('Erro ao conectar pontos:', error);
        // Recarregar em caso de erro
        await carregarGrafo();
    }
}

async function excluirPonto(nome) {
    if (!confirm(`Deseja realmente excluir o ponto "${nome}"?\n\nTodas as conexões deste ponto serão removidas.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/vertice/${nome}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            alert(error.erro || 'Erro ao excluir ponto');
            return;
        }
        
        const data = await response.json();
        state.points = data.grafo.vertices;
        state.edges = data.grafo.arestas;
        state.selectedPoint = null;
        state.optimizedPath = null;
        atualizarSelects();
        atualizarStatus(data.status);
        atualizarHint();
        fecharResultados();
        draw();
    } catch (error) {
        console.error('Erro ao excluir ponto:', error);
        await carregarGrafo();
    }
}

// Drawing
function draw() {
    const ctx = state.ctx;
    const width = state.canvas.width;
    const height = state.canvas.height;
    
    // Limpar canvas
    ctx.clearRect(0, 0, width, height);
    
    // Desenhar trajetórias normais
    if (state.edges && Array.isArray(state.edges) && state.edges.length > 0) {
        state.edges.forEach((edge) => {
            // Suportar tanto array [from, to] quanto objeto {origem, destino}
            let from, to;
            if (Array.isArray(edge)) {
                [from, to] = edge;
            } else if (edge.origem && edge.destino) {
                from = edge.origem;
                to = edge.destino;
            } else {
                return; // Formato desconhecido, pular
            }
            
            const p1 = state.points[from];
            const p2 = state.points[to];
            if (p1 && p2) {
                ctx.strokeStyle = '#9ca3af';
                ctx.setLineDash([5, 5]);
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            }
        });
    }
    
    // Desenhar linha temporária quando um ponto está selecionado no modo edge
    if (state.mode === 'edge' && state.selectedPoint && state.points[state.selectedPoint]) {
        const selectedPos = state.points[state.selectedPoint];
        const mousePos = state.lastMousePos || { x: selectedPos.x, y: selectedPos.y };
        
        ctx.strokeStyle = '#3b82f6';
        ctx.setLineDash([3, 3]);
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(selectedPos.x, selectedPos.y);
        ctx.lineTo(mousePos.x, mousePos.y);
        ctx.stroke();
        
        // Desenhar círculo no ponto de destino potencial
        const hoverPoint = encontrarPontoProximo(mousePos.x, mousePos.y);
        if (hoverPoint && hoverPoint !== state.selectedPoint) {
            const hoverPos = state.points[hoverPoint];
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2;
            ctx.setLineDash([]);
            ctx.beginPath();
            ctx.arc(hoverPos.x, hoverPos.y, 10, 0, Math.PI * 2);
            ctx.stroke();
        }
    }
    
    // Desenhar caminho otimizado
    if (state.optimizedPath && state.optimizedPath.length > 1) {
        // Determinar quantas linhas desenhar
        // Se está animando, só desenha até animationStep; senão, desenha todas
        const maxSteps = state.isAnimating ? state.animationStep : state.optimizedPath.length - 1;
        
        for (let i = 0; i < state.optimizedPath.length - 1; i++) {
            // Só desenha se i < maxSteps
            if (i >= maxSteps) {
                continue; // Pula esta linha se ainda não foi animada
            }
            
            const p1 = state.points[state.optimizedPath[i]];
            const p2 = state.points[state.optimizedPath[i + 1]];
            if (p1 && p2) {
                // Obter progresso de preenchimento desta linha (0-1)
                const lineProgress = state.lineProgress[i]?.progress ?? 1;
                
                // Calcular ponto final baseado no progresso
                const currentX = p1.x + (p2.x - p1.x) * lineProgress;
                const currentY = p1.y + (p2.y - p1.y) * lineProgress;
                
                // Linha vermelha destacada (mais grossa quando animando)
                ctx.setLineDash([]);
                ctx.strokeStyle = '#ef4444';
                ctx.lineWidth = state.isAnimating ? 5 : 4;
                ctx.lineCap = 'round'; // Ponta arredondada para melhor visualização
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(currentX, currentY);
                ctx.stroke();
                
                // Desenhar número apenas se a linha estiver completamente preenchida ou quase
                if (lineProgress >= 0.5) {
                    // Número da etapa com destaque
                    const midX = (p1.x + p2.x) / 2;
                    const midY = (p1.y + p2.y) / 2;
                    
                    // Fundo branco para destacar (com opacidade baseada no progresso)
                    const opacity = Math.min(lineProgress * 2, 1); // Aparece quando progresso >= 0.5
                    ctx.globalAlpha = opacity;
                    ctx.fillStyle = '#ffffff';
                    ctx.beginPath();
                    ctx.arc(midX, midY, 18, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // Borda preta
                    ctx.strokeStyle = '#000000';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                    
                    // Texto preto em negrito maior
                    ctx.fillStyle = '#000000';
                    ctx.font = 'bold 16px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(`N${i + 1}`, midX, midY);
                    ctx.globalAlpha = 1; // Resetar opacidade
                }
            }
        }
    }
    
    // Desenhar pontos
    ctx.setLineDash([]);
    Object.entries(state.points).forEach(([nome, pos]) => {
        let color = '#2563eb';
        let size = 8;
        
        if (nome === state.selectedPoint) {
            color = '#ef4444';
            size = 12;
        } else if (state.optimizedPath && nome === state.optimizedPath[0]) {
            color = '#10b981';
            size = 10;
        }
        
        // Círculo
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, size, 0, Math.PI * 2);
        ctx.fill();
        
        // Borda
        ctx.strokeStyle = color === '#2563eb' ? '#1e40af' : color === '#ef4444' ? '#dc2626' : '#059669';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Label
        ctx.fillStyle = '#1f2937';
        ctx.font = '600 11px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillText(nome, pos.x, pos.y - size - 4);
    });
}

// UI Updates
function atualizarSelects() {
    const fromSelect = document.getElementById('edge-from');
    const toSelect = document.getElementById('edge-to');
    
    [fromSelect, toSelect].forEach(select => {
        select.innerHTML = '<option value="">Selecione...</option>';
        Object.keys(state.points).forEach(nome => {
            const option = document.createElement('option');
            option.value = nome;
            option.textContent = nome;
            select.appendChild(option);
        });
    });
}

function atualizarStatus(status = null) {
    document.getElementById('num-points').textContent = Object.keys(state.points).length;
    document.getElementById('num-edges').textContent = state.edges.length;
    
    const statusText = document.getElementById('status-text');
    if (!status) {
        statusText.textContent = 'Aguardando...';
        statusText.className = 'status-waiting';
    } else if (status[0]) {
        statusText.textContent = '✅ Pronto para otimizar';
        statusText.className = 'status-ready';
    } else {
        statusText.textContent = `⚠️ ${status[1]}`;
        statusText.className = 'status-error';
    }
}

function mostrarResultados(data) {
    const panel = document.getElementById('results-panel');
    const stats = document.getElementById('results-stats');
    const code = document.getElementById('cnc-code');
    
    stats.innerHTML = `
        <div class="stat-item">
            <div class="stat-label">Distância Total</div>
            <div class="stat-value">${data.distancia.toFixed(2)} mm</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Tempo de Corte</div>
            <div class="stat-value">${data.tempo_corte.toFixed(2)} min</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Tempo Total</div>
            <div class="stat-value">${data.tempo_total.toFixed(2)} min</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Trajetórias</div>
            <div class="stat-value">${data.estatisticas.trajetorias_percorridas}</div>
        </div>
    `;
    
    code.textContent = data.programa_cnc;
    panel.classList.remove('hidden');
}

function fecharResultados() {
    document.getElementById('results-panel').classList.add('hidden');
}

function atualizarHint() {
    const hint = document.getElementById('canvas-hint');
    const numPoints = Object.keys(state.points).length;
    
    if (numPoints === 0) {
        hint.style.display = 'flex';
        if (state.mode === 'point') {
            hint.textContent = 'Clique para adicionar pontos de corte';
        } else {
            hint.textContent = 'Adicione pontos primeiro';
        }
    } else {
        hint.style.display = 'none';
    }
    
    // Atualizar botão de excluir
    const btnExcluir = document.getElementById('btn-excluir-ponto');
    if (btnExcluir) {
        if (state.selectedPoint) {
            btnExcluir.style.display = 'block';
            btnExcluir.textContent = `🗑️ Excluir "${state.selectedPoint}"`;
        } else {
            btnExcluir.style.display = 'none';
        }
    }
}

function excluirPontoSelecionado() {
    if (state.selectedPoint) {
        excluirPonto(state.selectedPoint);
    }
}

