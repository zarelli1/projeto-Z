/**
 * DashBot - Frontend Organizado
 * Classe principal para gerenciar toda a aplicação
 */

class NPSAnalyzer {
    constructor() {
        this.apiBaseUrl = this.detectApiUrl();
        this.currentStep = 1;
        this.analysisData = null;
        this.isProcessing = false;
        
        // Timeout configurations - escalonados
        this.timeouts = {
            test: 35000,        // 35s (5s buffer do backend)
            analysis: 125000,   // 125s (5s buffer do backend)
            retry_delay: 2000,  // 2s entre tentativas
            health_check: 5000  // 5s para health check
        };
        
        // DOM Elements Cache
        this.elements = this.cacheElements();
        
        // Initialize
        this.init();
    }

    /**
     * Detecta automaticamente a URL da API com fallbacks
     */
    detectApiUrl() {
        const currentHost = window.location.hostname;
        console.log('[DEBUG] Current host:', currentHost);
        console.log('[DEBUG] Current origin:', window.location.origin);
        
        // Se estiver executando localmente, usar localhost
        if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
            const currentPort = window.location.port || 3001;
            const url = `http://localhost:${currentPort}`;
            console.log('[DEBUG] Using localhost URL:', url);
            return url;
        }
        
        // Para Vercel/produção, usar o host atual sem porta
        const url = window.location.origin;
        console.log('[DEBUG] Using production URL:', url);
        return url;
    }

    /**
     * Encontra porta ativa do servidor
     */
    async findActivePort() {
        const ports = [3001, 3002, 3003, 3004];
        
        for (const port of ports) {
            try {
                const response = await fetch(`http://localhost:${port}/api/health`, {
                    method: 'GET',
                    signal: AbortSignal.timeout(2000)
                });
                if (response.ok) {
                    this.apiBaseUrl = `http://localhost:${port}`;
                    return port;
                }
            } catch (e) {
                continue;
            }
        }
        throw new Error('Nenhum servidor encontrado nas portas: ' + ports.join(', '));
    }

    /**
     * Cache de elementos DOM para melhor performance
     */
    cacheElements() {
        return {
            // Steps
            stepsIndicator: document.querySelectorAll('.step'),
            stepContents: document.querySelectorAll('.step-content'),
            
            // Server Status
            serverStatus: document.getElementById('server-status'),
            statusIndicator: document.getElementById('status-indicator'),
            statusText: document.getElementById('status-text'),
            
            // Form Elements
            projectName: document.getElementById('project-name'),
            sheetsUrl: document.getElementById('sheets-url'),
            fileInput: document.getElementById('file-input'),
            fileUpload: document.getElementById('file-upload'),
            fileInfo: document.getElementById('file-info'),
            
            // Method Selection
            methodButtons: document.querySelectorAll('.method-btn'),
            urlMethod: document.getElementById('url-method'),
            fileMethod: document.getElementById('file-method'),
            
            // Advanced Options
            advancedToggle: document.getElementById('advanced-toggle'),
            advancedContent: document.getElementById('advanced-content'),
            enableDateFilter: document.getElementById('enable-date-filter'),
            dateFilter: document.getElementById('date-filter'),
            dateStart: document.getElementById('date-start'),
            dateEnd: document.getElementById('date-end'),
            
            // Buttons
            testUrl: document.getElementById('test-url'),
            startAnalysis: document.getElementById('start-analysis'),
            cancelAnalysis: document.getElementById('cancel-analysis'),
            downloadReport: document.getElementById('download-report'),
            newAnalysis: document.getElementById('new-analysis'),
            removeFile: document.getElementById('remove-file'),
            
            // Progress
            progressFill: document.getElementById('progress-fill'),
            progressText: document.getElementById('progress-text'),
            progressPercentage: document.getElementById('progress-percentage'),
            processingSteps: {
                extract: document.getElementById('step-extract'),
                analyze: document.getElementById('step-analyze'),
                generate: document.getElementById('step-generate')
            },
            
            // Results
            npsScore: document.getElementById('nps-score'),
            totalResponses: document.getElementById('total-responses'),
            avgRating: document.getElementById('avg-rating'),
            totalSellers: document.getElementById('total-sellers'),
            reportFilename: document.getElementById('report-filename'),
            reportDescription: document.getElementById('report-description'),
            
            // Messages
            messageContainer: document.getElementById('message-container'),
            loadingOverlay: document.getElementById('loading-overlay')
        };
    }

    /**
     * Inicialização da aplicação
     */
    async init() {
        this.setupEventListeners();
        
        // Tenta detectar porta ativa se localhost
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            try {
                await this.findActivePort();
                console.log('[API] Porta detectada:', this.apiBaseUrl);
            } catch (error) {
                console.warn('[API] Erro na detecção de porta:', error.message);
            }
        }
        
        await this.checkServerStatus();
        this.updateStepIndicator();
        
        console.log('[NPSAnalyzer] Sistema inicializado');
        console.log('[API] Base URL:', this.apiBaseUrl);
    }

    /**
     * Configuração de event listeners
     */
    setupEventListeners() {
        // Method selection
        this.elements.methodButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.selectInputMethod(e.target.dataset.method));
        });

        // File upload
        this.elements.fileUpload.addEventListener('click', () => this.elements.fileInput.click());
        this.elements.fileUpload.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.elements.fileUpload.addEventListener('drop', (e) => this.handleFileDrop(e));
        this.elements.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.elements.removeFile.addEventListener('click', () => this.removeSelectedFile());

        // Advanced options
        this.elements.advancedToggle.addEventListener('click', () => this.toggleAdvancedOptions());
        this.elements.enableDateFilter.addEventListener('change', () => this.toggleDateFilter());

        // Buttons
        this.elements.testUrl.addEventListener('click', () => this.testConnection());
        this.elements.startAnalysis.addEventListener('click', () => this.startAnalysis());
        this.elements.cancelAnalysis.addEventListener('click', () => this.cancelAnalysis());
        this.elements.downloadReport.addEventListener('click', () => this.downloadReport());
        this.elements.newAnalysis.addEventListener('click', () => this.startNewAnalysis());

        // Real-time validation
        this.elements.sheetsUrl.addEventListener('input', () => this.validateSheetsUrl());
        this.elements.projectName.addEventListener('input', () => this.validateForm());
    }

    /**
     * Verifica status do servidor
     */
    async checkServerStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/health`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                signal: AbortSignal.timeout(this.timeouts.health_check)
            });

            if (response.ok) {
                const data = await response.json();
                this.updateServerStatus('online', `Servidor Online - ${data.version}`);
                return true;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            this.updateServerStatus('offline', 'Servidor Offline');
            this.showMessage('Erro de conexão com o servidor', 'error');
            return false;
        }
    }

    /**
     * Atualiza indicador de status do servidor
     */
    updateServerStatus(status, text) {
        this.elements.statusIndicator.className = `status-indicator ${status}`;
        this.elements.statusText.textContent = text;
    }

    /**
     * Seleção do método de input
     */
    selectInputMethod(method) {
        // Update buttons
        this.elements.methodButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.method === method);
        });

        // Show/hide method sections
        if (method === 'url') {
            this.elements.urlMethod.classList.remove('hidden');
            this.elements.fileMethod.classList.add('hidden');
        } else {
            this.elements.urlMethod.classList.add('hidden');
            this.elements.fileMethod.classList.remove('hidden');
        }
    }

    /**
     * Drag and drop handlers
     */
    handleDragOver(e) {
        e.preventDefault();
        this.elements.fileUpload.classList.add('dragover');
    }

    handleFileDrop(e) {
        e.preventDefault();
        this.elements.fileUpload.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        if (e.target.files.length > 0) {
            this.processFile(e.target.files[0]);
        }
    }

    /**
     * Processa arquivo selecionado
     */
    processFile(file) {
        // Validate file
        if (!file.name.toLowerCase().endsWith('.csv')) {
            this.showMessage('Apenas arquivos CSV são aceitos', 'error');
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB
            this.showMessage('Arquivo muito grande. Máximo 10MB', 'error');
            return;
        }

        // Show file info
        this.elements.fileUpload.querySelector('.upload-content').classList.add('hidden');
        this.elements.fileInfo.classList.remove('hidden');
        this.elements.fileInfo.querySelector('.file-name').textContent = file.name;
        this.elements.fileInfo.querySelector('.file-size').textContent = this.formatFileSize(file.size);

        this.selectedFile = file;
        this.validateForm();
    }

    /**
     * Remove arquivo selecionado
     */
    removeSelectedFile() {
        this.elements.fileUpload.querySelector('.upload-content').classList.remove('hidden');
        this.elements.fileInfo.classList.add('hidden');
        this.elements.fileInput.value = '';
        this.selectedFile = null;
        this.validateForm();
    }

    /**
     * Toggle opções avançadas
     */
    toggleAdvancedOptions() {
        const isHidden = this.elements.advancedContent.classList.contains('hidden');
        this.elements.advancedContent.classList.toggle('hidden');
        
        const icon = this.elements.advancedToggle.querySelector('.fa-chevron-down');
        icon.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
    }

    /**
     * Toggle filtro de data
     */
    toggleDateFilter() {
        const isEnabled = this.elements.enableDateFilter.checked;
        this.elements.dateFilter.classList.toggle('hidden', !isEnabled);
    }

    /**
     * Validação da URL do Google Sheets
     * CORREÇÃO: Usa setTimeout para quebrar a recursão infinita
     */
    validateSheetsUrl() {
        const url = this.elements.sheetsUrl.value.trim();
        const isValid = url === '' || /^https:\/\/docs\.google\.com\/spreadsheets\/d\/[a-zA-Z0-9-_]+/.test(url);
        
        this.elements.sheetsUrl.classList.toggle('invalid', !isValid);
        
        // CORREÇÃO: Chama validateForm de forma assíncrona para evitar stack overflow
        setTimeout(() => this.validateForm(), 0);
        
        return isValid;
    }

    /**
     * Validação geral do formulário
     * CORREÇÃO: Removida chamada recursiva para validateSheetsUrl() para evitar loop infinito
     */
    validateForm() {
        const projectName = this.elements.projectName.value.trim();
        const hasUrl = this.elements.sheetsUrl.value.trim() !== '';
        const hasFile = this.selectedFile !== null;
        
        // CORREÇÃO: Validação de URL inline para evitar recursão
        const url = this.elements.sheetsUrl.value.trim();
        const isUrlValid = url === '' || /^https:\/\/docs\.google\.com\/spreadsheets\/d\/[a-zA-Z0-9-_]+/.test(url);
        
        const isUrlMethod = this.elements.urlMethod.classList.contains('hidden') === false;
        const isValid = projectName && ((isUrlMethod && hasUrl && isUrlValid) || (!isUrlMethod && hasFile));
        
        this.elements.startAnalysis.disabled = !isValid;
    }

    /**
     * Testa conexão com a planilha
     */
    async testConnection() {
        const url = this.elements.sheetsUrl.value.trim();
        if (!url) {
            this.showMessage('Digite a URL da planilha', 'warning');
            return;
        }

        this.elements.testUrl.disabled = true;
        this.elements.testUrl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testando...';

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sheets_url: url }),
                signal: AbortSignal.timeout(this.timeouts.test)
            });

            // CORREÇÃO: Verificar status da resposta antes de tentar fazer parse do JSON
            if (!response.ok) {
                throw new Error(`Erro do servidor: ${response.status} ${response.statusText}`);
            }

            let data;
            try {
                // CORREÇÃO: Proteção contra JSON malformado
                data = await response.json();
            } catch (jsonError) {
                console.error('[API Error] Resposta não é JSON válido:', jsonError);
                throw new Error('Resposta inválida do servidor');
            }
            
            if (data.success) {
                this.showMessage(`Conexão OK! ${data.message || 'Planilha acessível'}`, 'success');
            } else {
                this.showMessage(`Erro: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('[Test Connection] Erro completo:', error);
            this.showMessage(`Erro na conexão: ${error.message}`, 'error');
        } finally {
            this.elements.testUrl.disabled = false;
            this.elements.testUrl.innerHTML = '<i class="fas fa-check-circle"></i> Testar Conexão';
        }
    }

    /**
     * Inicia análise
     */
    async startAnalysis() {
        if (this.isProcessing) return;

        this.isProcessing = true;
        this.goToStep(2);
        this.resetProgress();

        const formData = this.getFormData();
        
        try {
            await this.performAnalysis(formData);
        } catch (error) {
            console.error('[Analysis Error]', error);
            this.showMessage('Erro na análise: ' + error.message, 'error');
            this.goToStep(1);
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Coleta dados do formulário
     */
    getFormData() {
        const isUrlMethod = !this.elements.urlMethod.classList.contains('hidden');
        
        const data = {
            loja_nome: this.elements.projectName.value.trim(),
            estilo_pdf: 'mdo_weasy'
        };

        if (isUrlMethod) {
            data.sheets_url = this.elements.sheetsUrl.value.trim();
        }

        // Date filter
        if (this.elements.enableDateFilter.checked) {
            if (this.elements.dateStart.value) data.data_inicio = this.elements.dateStart.value;
            if (this.elements.dateEnd.value) data.data_fim = this.elements.dateEnd.value;
        }

        return { data, isUrlMethod, file: this.selectedFile };
    }

    /**
     * Executa análise
     */
    async performAnalysis(formData) {
        this.updateProgress(5, 'Iniciando análise...');
        this.updateProcessingStep('extract', 'processing');

        let response;
        
        if (formData.isUrlMethod) {
            // URL method with timeout
            response = await fetch(`${this.apiBaseUrl}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData.data),
                signal: AbortSignal.timeout(this.timeouts.analysis)
            });
        } else {
            // File method with timeout
            const form = new FormData();
            form.append('file', formData.file);
            form.append('nome_loja', formData.data.loja_nome);
            form.append('usar_looker', 'false');
            form.append('gerar_ia', 'true');
            form.append('estilo_pdf', formData.data.estilo_pdf);

            response = await fetch(`${this.apiBaseUrl}/api/analyze`, {
                method: 'POST',
                body: form,
                signal: AbortSignal.timeout(this.timeouts.analysis)
            });
        }

        // Progress simulation
        this.simulateProgress();

        // CORREÇÃO: Verificar status da resposta antes de tentar fazer parse do JSON
        if (!response.ok) {
            throw new Error(`Erro do servidor: ${response.status} ${response.statusText}`);
        }

        let result;
        try {
            // CORREÇÃO: Proteção contra JSON malformado na análise
            result = await response.json();
        } catch (jsonError) {
            console.error('[Analysis Error] Resposta não é JSON válido:', jsonError);
            throw new Error('Resposta inválida do servidor durante análise');
        }
        
        if (!result) {
            throw new Error(result.error || `HTTP ${response.status}`);
        }

        if (result.success) {
            this.analysisData = result;
            this.completeAnalysis();
        } else {
            throw new Error(result.error || 'Análise falhou');
        }
    }

    /**
     * Simula progresso da análise
     */
    simulateProgress() {
        let progress = 10;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            
            let text = 'Processando...';
            if (progress < 30) {
                text = 'Extraindo dados...';
                this.updateProcessingStep('extract', 'processing');
            } else if (progress < 70) {
                text = 'Analisando com IA...';
                this.updateProcessingStep('extract', 'completed');
                this.updateProcessingStep('analyze', 'processing');
            } else {
                text = 'Gerando relatório...';
                this.updateProcessingStep('analyze', 'completed');
                this.updateProcessingStep('generate', 'processing');
            }
            
            this.updateProgress(progress, text);
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 800);
    }

    /**
     * Completa análise
     */
    completeAnalysis() {
        this.updateProgress(100, 'Análise concluída!');
        this.updateProcessingStep('generate', 'completed');
        
        setTimeout(() => {
            this.displayResults();
            this.goToStep(3);
        }, 1500);
    }

    /**
     * Exibe resultados
     */
    displayResults() {
        const data = this.analysisData.dados || {};
        
        // Animate metrics
        this.animateMetric(this.elements.npsScore, data.nps_score || 0, '%');
        this.animateMetric(this.elements.totalResponses, data.total_registros || 0);
        this.animateMetric(this.elements.avgRating, data.avg_rating || 0, '/10');
        this.animateMetric(this.elements.totalSellers, data.vendedores || 0);
        
        // Report info
        this.elements.reportFilename.textContent = this.analysisData.arquivo || 'relatorio_nps.docx';
        this.elements.reportDescription.textContent = this.analysisData.message || 'Relatório gerado com sucesso';
    }

    /**
     * Anima métricas
     */
    animateMetric(element, targetValue, suffix = '') {
        let currentValue = 0;
        const increment = targetValue / 30;
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            
            const displayValue = suffix === '/10' ? currentValue.toFixed(1) : Math.floor(currentValue);
            element.textContent = displayValue + suffix;
        }, 50);
    }

    /**
     * Atualiza progresso
     */
    updateProgress(percentage, text) {
        this.elements.progressFill.style.width = percentage + '%';
        this.elements.progressText.textContent = text;
        this.elements.progressPercentage.textContent = Math.round(percentage) + '%';
    }

    /**
     * Atualiza step de processamento
     */
    updateProcessingStep(stepName, status) {
        const step = this.elements.processingSteps[stepName];
        if (!step) return;

        const statusIcon = step.querySelector('.step-status i');
        statusIcon.className = 'fas ' + {
            'waiting': 'fa-clock',
            'processing': 'fa-spinner fa-spin',
            'completed': 'fa-check-circle'
        }[status];

        step.className = `processing-step ${status}`;
    }

    /**
     * Reset progresso
     */
    resetProgress() {
        this.updateProgress(0, 'Iniciando...');
        Object.keys(this.elements.processingSteps).forEach(step => {
            this.updateProcessingStep(step, 'waiting');
        });
    }

    /**
     * Download do relatório
     */
    downloadReport() {
        if (!this.analysisData || !this.analysisData.arquivo) {
            this.showMessage('Nenhum relatório disponível', 'error');
            return;
        }

        const link = document.createElement('a');
        link.href = `${this.apiBaseUrl}/relatorios/${this.analysisData.arquivo}`;
        link.download = this.analysisData.arquivo;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        this.showMessage('Download iniciado!', 'success');
    }

    /**
     * Cancela análise
     */
    cancelAnalysis() {
        if (this.isProcessing) {
            this.isProcessing = false;
            this.goToStep(1);
            this.showMessage('Análise cancelada', 'info');
        }
    }

    /**
     * Inicia nova análise
     */
    startNewAnalysis() {
        this.goToStep(1);
        this.analysisData = null;
        this.elements.projectName.value = 'Análise NPS';
        this.elements.sheetsUrl.value = '';
        this.removeSelectedFile();
        this.elements.enableDateFilter.checked = false;
        this.toggleDateFilter();
    }

    /**
     * Navega para step
     */
    goToStep(stepNumber) {
        this.currentStep = stepNumber;
        this.updateStepIndicator();
        
        // Hide all step contents
        this.elements.stepContents.forEach(content => {
            content.classList.remove('active');
        });
        
        // Show current step
        document.getElementById(`step-${stepNumber}`).classList.add('active');
    }

    /**
     * Atualiza indicador de steps
     */
    updateStepIndicator() {
        this.elements.stepsIndicator.forEach((step, index) => {
            const stepNumber = index + 1;
            step.classList.toggle('active', stepNumber === this.currentStep);
            step.classList.toggle('completed', stepNumber < this.currentStep);
        });
    }

    /**
     * Mostra mensagem
     */
    showMessage(text, type = 'info') {
        const message = document.createElement('div');
        message.className = `message ${type}`;
        message.innerHTML = `
            <i class="fas ${this.getMessageIcon(type)}"></i>
            <span>${text}</span>
            <button class="close-message"><i class="fas fa-times"></i></button>
        `;

        message.querySelector('.close-message').addEventListener('click', () => {
            message.remove();
        });

        this.elements.messageContainer.appendChild(message);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (message.parentNode) {
                message.remove();
            }
        }, 5000);
    }

    /**
     * Ícone da mensagem
     */
    getMessageIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * Formata tamanho do arquivo
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.npsAnalyzer = new NPSAnalyzer();
});