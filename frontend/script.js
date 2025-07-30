// Elementos do DOM - Cache otimizado
const elements = {
    analyzeBtn: document.getElementById('analyze-btn'),
    sheetsUrl: document.getElementById('sheets-url'),
    lojaNome: document.getElementById('loja-nome'),
    errorMessage: document.getElementById('error-message'),
    loadingContainer: document.getElementById('loading-container'),
    resultsContainer: document.getElementById('results-container'),
    multiResultsContainer: document.getElementById('multi-results-container'),
    progressFill: document.getElementById('progress-fill'),
    progressText: document.getElementById('progress-text'),
    downloadPdf: document.getElementById('download-pdf'),
    downloadExcel: document.getElementById('download-excel'),
    
    // Métricas
    npsScore: document.getElementById('nps-score'),
    totalResponses: document.getElementById('total-responses'),
    avgRating: document.getElementById('avg-rating'),
    vendedores: document.getElementById('vendedores'),
    
    // Multi-sheet elements
    multiTotalSheets: document.getElementById('multi-total-sheets'),
    multiTotalRecords: document.getElementById('multi-total-records'),
    multiAvgNps: document.getElementById('multi-avg-nps'),
    sheetResults: document.getElementById('sheet-results'),
    downloadAllPdfs: document.getElementById('download-all-pdfs')
};

// Estados da aplicação
let isProcessing = false;
let currentReportFile = null;
let progressInterval = null;

// Validação de URL do Google Sheets
function isValidGoogleSheetsUrl(url) {
    const pattern = /^https:\/\/docs\.google\.com\/spreadsheets\/d\/[a-zA-Z0-9-_]+/;
    return pattern.test(url);
}

// Mostrar erro - Otimizado
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.style.display = 'block';
    setTimeout(() => {
        elements.errorMessage.style.display = 'none';
    }, 5000);
}

// Esconder todos os containers - Otimizado
function hideAllContainers() {
    elements.loadingContainer.style.display = 'none';
    elements.resultsContainer.style.display = 'none';
    elements.multiResultsContainer.style.display = 'none';
}

// Progress inteligente baseado em tempo real
function updateProgress(percentage, text) {
    elements.progressFill.style.width = percentage + '%';
    elements.progressText.textContent = text;
}

// Progress realístico sincronizado com backend
function startProgressTracking() {
    let progress = 5;
    const maxTime = 120000; // 2 minutos máximo
    const startTime = Date.now();
    
    // Limpar interval anterior se existir
    if (progressInterval) clearInterval(progressInterval);
    
    progressInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const timeProgress = Math.min((elapsed / maxTime) * 85, 85); // Máximo 85% baseado no tempo
        
        // Usa o maior valor entre progresso manual e baseado em tempo
        progress = Math.max(progress, timeProgress);
        
        // Atualiza UI
        updateProgress(Math.min(progress, 90), getProgressText(progress));
        
        // Para quando alcança 90% (aguarda resposta real)
        if (progress >= 90) {
            clearInterval(progressInterval);
        }
    }, 1000);
}

function getProgressText(progress) {
    if (progress < 15) return 'Conectando com backend...';
    if (progress < 30) return 'Acessando Google Sheets...';
    if (progress < 45) return 'Extraindo dados da planilha...';
    if (progress < 60) return 'Processando com IA OpenAI...';
    if (progress < 75) return 'Calculando métricas de pós-venda...';
    if (progress < 90) return 'Gerando relatório PDF...';
    return 'Finalizando análise...';
}

// Animar números - Otimizado
function animateNumber(element, start, end, duration = 800) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = start + (end - start) * progress;
        
        // Formatação inteligente baseada no elemento
        if (element === elements.avgRating) {
            element.textContent = current.toFixed(1);
        } else {
            element.textContent = Math.floor(current);
        }
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Mostrar resultados reais - Sincronizado com backend
function showRealResults(metrics) {
    // Para progress tracking
    if (progressInterval) clearInterval(progressInterval);
    
    updateProgress(100, 'Análise concluída!');
    
    setTimeout(() => {
        elements.loadingContainer.style.display = 'none';
        elements.resultsContainer.style.display = 'block';
        
        // Animar métricas com valores reais do backend
        setTimeout(() => {
            animateNumber(elements.npsScore, 0, metrics.nps_score || 0);
            animateNumber(elements.totalResponses, 0, metrics.total_responses || 0);
            animateNumber(elements.avgRating, 0, metrics.avg_rating || 0);
            animateNumber(elements.vendedores, 0, metrics.vendedores || 0);
        }, 200);
        
        // Reset botão
        resetAnalyzeButton();
    }, 500);
}

// Reset do botão de análise
function resetAnalyzeButton() {
    isProcessing = false;
    elements.analyzeBtn.disabled = false;
    elements.analyzeBtn.innerHTML = '<i class="fas fa-chart-line"></i> Analisar Pós-Venda';
}

// Processar análise - Otimizado e sincronizado
async function processAnalysis() {
    const url = elements.sheetsUrl.value.trim();
    const loja = elements.lojaNome.value.trim() || 'SocialZap';
    const estilo = 'mdo_weasy'; // Fixo no estilo MDO com emojis reais
    
    // Validação rápida
    if (!url) {
        showError('Por favor, insira a URL do Google Sheets');
        return;
    }
    
    if (!isValidGoogleSheetsUrl(url)) {
        showError('URL inválida. Use uma URL válida do Google Sheets');
        return;
    }
    
    // Bloquear interface
    isProcessing = true;
    elements.analyzeBtn.disabled = true;
    elements.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
    
    // Mostrar loading
    hideAllContainers();
    elements.loadingContainer.style.display = 'block';
    
    // Iniciar tracking inteligente
    updateProgress(0, 'Iniciando análise...');
    
    try {
        // Health check rápido
        updateProgress(5, 'Verificando servidor...');
        const isServerRunning = await dashBotAPI.healthCheck();
        if (!isServerRunning) {
            throw new Error('Servidor backend não está rodando. Execute: python frontend/server.py');
        }
        
        // Iniciar progress tracking
        startProgressTracking();
        
        // Executar análise real do backend
        const result = await dashBotAPI.analyzeNPS(url, loja, estilo);
        
        if (result.success) {
            // Sempre usar resultado único com relatório executivo simples
            currentReportFile = result.arquivo || result.file_name;
            
            // Preparar dados do relatório único
            const dadosRelatorio = {
                nps_score: result.dados?.nps_score || 0,
                total_avaliacoes: result.dados?.total_registros || 0,
                download_url: result.download_url,
                arquivo: result.arquivo
            };
            
            showSingleReport(dadosRelatorio);
        } else {
            throw new Error(result.error || 'Erro na análise de pós-venda');
        }
        
    } catch (error) {
        console.error('Erro na análise:', error);
        
        // Para progress tracking
        if (progressInterval) clearInterval(progressInterval);
        
        // Mostra erro específico
        const errorMsg = error.message.includes('timeout') 
            ? 'Análise demorou muito. Planilha muito grande ou problemas de conectividade.'
            : `Erro na análise: ${error.message}`;
            
        showError(errorMsg);
        
        // Reset estado
        resetAnalyzeButton();
        hideAllContainers();
    }
}

// Download do PDF real - SOLUÇÃO MELHORADA
function downloadPdfReport() {
    if (!currentReportFile) {
        showError('Nenhum relatório disponível para download');
        return;
    }
    
    // Feedback visual inicial
    const originalText = elements.downloadPdf.innerHTML;
    elements.downloadPdf.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Baixando...';
    elements.downloadPdf.disabled = true;
    
    try {
        // Método direto e simples
        const link = document.createElement('a');
        link.href = `/relatorios/${currentReportFile}`;
        link.download = currentReportFile;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Feedback de sucesso
        elements.downloadPdf.innerHTML = '<i class="fas fa-check"></i> Baixado!';
        elements.downloadPdf.style.backgroundColor = '#10B981';
        
        setTimeout(() => {
            elements.downloadPdf.innerHTML = originalText;
            elements.downloadPdf.style.backgroundColor = '';
            elements.downloadPdf.disabled = false;
        }, 2000);
        
        console.log(`✅ Download iniciado: ${currentReportFile}`);
        
    } catch (error) {
        console.error('Erro no download:', error);
        showError('Erro ao baixar PDF: ' + error.message);
        
        // Restaurar botão
        elements.downloadPdf.innerHTML = originalText;
        elements.downloadPdf.disabled = false;
    }
}

// Simular download de Excel
function downloadExcelReport() {
    // Dados simulados em formato CSV
    const csvContent = `Data,Nome,Loja,Vendedor,Avaliacao
2024-01-15,"João Silva","Loja Centro","Maria Santos",9
2024-01-16,"Ana Costa","Loja Norte","Pedro Lima",8
2024-01-17,"Carlos Souza","Loja Sul","Ana Paula",10
2024-01-18,"Lucia Fernandes","Loja Centro","Maria Santos",7
2024-01-19,"Roberto Alves","Loja Norte","Pedro Lima",9`;

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `dados_nps_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    // Feedback visual
    const originalText = downloadExcel.innerHTML;
    downloadExcel.innerHTML = '<i class="fas fa-check"></i> Baixado!';
    downloadExcel.style.backgroundColor = '#10B981';
    
    setTimeout(() => {
        downloadExcel.innerHTML = originalText;
        downloadExcel.style.backgroundColor = '';
    }, 2000);
}

// Event listeners otimizados
function initializeEventListeners() {
    // Botões principais
    elements.analyzeBtn.addEventListener('click', processAnalysis);
    elements.downloadPdf.addEventListener('click', downloadPdfReport);
    elements.downloadExcel.addEventListener('click', downloadExcelReport);

    // Validação em tempo real otimizada
    elements.sheetsUrl.addEventListener('input', debounce(function() {
        const url = this.value.trim();
        if (url && !isValidGoogleSheetsUrl(url)) {
            this.style.borderColor = '#EF4444';
            showError('URL deve ser do Google Sheets');
        } else {
            this.style.borderColor = 'rgba(251, 191, 36, 0.3)';
            elements.errorMessage.style.display = 'none';
        }
    }, 300));

    // Enter para analisar
    elements.sheetsUrl.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !isProcessing) {
            processAnalysis();
        }
    });
}

// Debounce para otimizar performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Inicialização quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    
    // URL de exemplo para pós-venda
    elements.sheetsUrl.placeholder = 'https://docs.google.com/spreadsheets/d/[ID]/edit...';
    
    console.log('🚀 Frontend SOCIALZAP Analista de Dash inicializado');
});

// Função para exibir resultado único (relatório executivo simples)
function showSingleReport(data) {
    try {
        hideAllContainers();
        elements.multiResultsContainer.style.display = 'block';
        
        // Animar métricas principais - ajustar para relatório único
        animateNumber(elements.multiTotalSheets, 0, 1); // Sempre 1 relatório
        animateNumber(elements.multiTotalRecords, 0, data.total_avaliacoes);
        animateNumber(elements.multiAvgNps, 0, data.nps_score);
        
        // Limpar resultados anteriores
        elements.sheetResults.innerHTML = '';
        
        // Criar card único para o relatório executivo
        const reportCard = document.createElement('div');
        reportCard.className = 'sheet-card';
        reportCard.innerHTML = `
            <div class="sheet-header">
                <h4>📊 Relatório NPS Executivo</h4>
                <span class="sheet-nps nps-${getNPSClass(data.nps_score)}">${data.nps_score}</span>
            </div>
            <div class="sheet-metrics">
                <span>${data.total_avaliacoes} avaliações analisadas</span>
                <span>Relatório profissional gerado</span>
            </div>
        `;
        elements.sheetResults.appendChild(reportCard);
        
        // Configurar botão de download único
        if (data.arquivo) {
            elements.downloadAllPdfs.onclick = () => downloadSingleFile(data.arquivo);
        }
        
        console.log('✅ Relatório executivo simples exibido');
        
    } catch (error) {
        console.error('Erro ao exibir relatório:', error);
        showError('Erro ao exibir relatório');
    }
}

// Função para classificar NPS
function getNPSClass(nps) {
    if (nps >= 50) return 'good';
    if (nps >= 0) return 'neutral';
    return 'bad';
}

// Função para download de arquivo único
function downloadSingleFile(fileName) {
    try {
        // Download direto via link
        const link = document.createElement('a');
        link.href = `/relatorios/${fileName}`;
        link.download = fileName;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        console.log(`✅ Download iniciado: ${fileName}`);
    } catch (error) {
        console.error('Erro no download:', error);
        // Fallback: abrir em nova aba
        window.open(`/relatorios/${fileName}`, '_blank');
    }
}

// Função para download de todos os arquivos - MELHORADA
function downloadAllFiles(files) {
    if (!files || files.length === 0) {
        showError('Nenhum arquivo disponível para download');
        return;
    }
    
    console.log(`📥 Iniciando download de ${files.length} arquivo(s)`);
    
    files.forEach((fileName, index) => {
        setTimeout(() => {
            // Download direto via link
            const link = document.createElement('a');
            link.href = `/relatorios/${fileName}`;
            link.download = fileName;
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            console.log(`✅ Download iniciado: ${fileName}`);
        }, index * 1000); // Delay para evitar bloqueio
    });
}