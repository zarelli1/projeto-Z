# 🚀 DashBot SocialZap - Frontend

Frontend moderno para automação de análise NPS integrado com o backend Python.

## 🎯 **Funcionalidades**

- ✅ **Interface moderna** com design dark/yellow
- ✅ **Validação de URL** do Google Sheets em tempo real
- ✅ **Loading realista** com progresso animado
- ✅ **Integração real** com backend Python
- ✅ **Download de PDF** gerado pela automação
- ✅ **Responsivo** mobile e desktop
- ✅ **Métricas animadas** NPS, respostas, nota média

## 🛠️ **Como Usar**

### **1. Iniciar o Servidor**
```bash
cd frontend
python server.py
```

### **2. Acessar Interface**
- Navegador abre automaticamente em: `http://localhost:8080`
- Ou acesse manualmente no navegador

### **3. Analisar Planilha**
1. **Nome da Loja**: Digite o nome (ex: "MDO Colombo")
2. **URL do Google Sheets**: Cole a URL da planilha
3. **Clique em "Analisar Dashboard"**
4. **Aguarde o processamento** (análise real é executada)
5. **Baixe o PDF** gerado

## 📁 **Estrutura**

```
frontend/
├── index.html      # Interface principal
├── style.css       # Estilos modernos
├── script.js       # Lógica do frontend
├── api.js         # Integração com backend
├── server.py      # Servidor local
└── README.md      # Este arquivo
```

## 🔧 **Recursos Técnicos**

- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Backend**: Python 3 com integração NPS
- **Servidor**: HTTP Server nativo do Python
- **Responsivo**: CSS Grid e Flexbox
- **Ícones**: Font Awesome 6
- **Animações**: CSS3 + JavaScript

## 🎨 **Design System**

- **Fundo**: Gradiente escuro (#0f0f0f → #1a1a1a)
- **Destaque**: Amarelo (#FBBF24)
- **Sucesso**: Verde (#10B981)
- **Erro**: Vermelho (#EF4444)
- **Texto**: Branco/Cinza claro

## 🚨 **Requisitos**

1. **Backend funcionando**: Sistema NPS em `/nps_automation/`
2. **Python 3.x**: Para executar o servidor
3. **Navegador moderno**: Chrome, Firefox, Safari, Edge
4. **Planilha pública**: URL do Google Sheets acessível

## 📊 **Fluxo de Uso**

1. **Usuário** insere URL e nome da loja
2. **Frontend** valida dados e envia para API
3. **Servidor** executa análise Python real
4. **Backend** gera PDF na pasta `relatorios/`
5. **Frontend** exibe métricas e permite download
6. **Usuário** baixa relatório PDF completo

## 🔄 **Integração com Backend**

O frontend se conecta diretamente com:
- `nps_extractor.py` - Extração de dados
- `calculadora_metricas.py` - Cálculo de NPS
- `gerador_relatorio_pdf.py` - Geração de PDF

**Resultado**: Análise real de dados NPS com download de relatório PDF profissional.

## 🎉 **Pronto Para Produção**

Interface completa e funcional integrada com sua automação Python existente!