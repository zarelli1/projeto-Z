// API para integração com backend Python
class DashBotAPI {
    constructor() {
        this.baseUrl = 'http://localhost:8080';
    }

    // Analisar dados - Analista de Dash GPT-4o
    async analyzeNPS(sheetsUrl, lojaName = 'Análise Dash', estiloPdf = 'mdo_weasy') {
        try {
            console.log('📡 Iniciando análise com Analista de Dash...');
            console.log('🔗 URL:', sheetsUrl);
            console.log('🏢 Projeto:', lojaName);
            
            // Timeout otimizado para análise IA (3 minutos)
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 180000); // 3 minutos
            
            const startTime = Date.now();
            
            const response = await fetch(`${this.baseUrl}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sheets_url: sheetsUrl,
                    loja_nome: lojaName,
                    estilo_pdf: estiloPdf
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            
            const elapsed = Date.now() - startTime;
            console.log(`⏱️ Análise concluída em ${(elapsed/1000).toFixed(1)}s`);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Erro no servidor: ${errorText}`);
            }

            const result = await response.json();
            console.log('✅ Análise recebida:', result);
            
            return result;

        } catch (error) {
            if (error.name === 'AbortError') {
                console.error('⏰ Timeout na análise');
                throw new Error('Análise demorou muito (máximo 3 minutos). Verifique a planilha.');
            }
            console.error('❌ Erro na API:', error);
            throw error;
        }
    }

    // Download de arquivo PDF
    async downloadPDF(fileName) {
        try {
            const response = await fetch(`${this.baseUrl}/relatorios/${fileName}`);
            
            if (!response.ok) {
                throw new Error(`Erro ao baixar PDF: ${response.status}`);
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            return true;

        } catch (error) {
            console.error('Erro no download:', error);
            return false;
        }
    }

    // Verificar status do servidor
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/`);
            return response.ok;
        } catch (error) {
            return false;
        }
    }
}

// Instância global da API
const dashBotAPI = new DashBotAPI();