# 🎯 PROCESSO COMPLETO DO SEU SISTEMA NPS AUTOMATION

## 📋 **FLUXO PRINCIPAL - COMO FUNCIONA O SISTEMA TODO**

### **🎬 INÍCIO: Usuário acessa o sistema**
```
💻 OPÇÕES DE ACESSO:
├── 🖥️ CLI: python3 main.py
└── 🌐 WEB: python3 frontend/server.py → http://localhost:8080
```

---

## 🔄 **PROCESSO COMPLETO PASSO A PASSO**

### **ETAPA 1: 📥 ENTRADA DE DADOS**
```
👤 Usuário fornece:
├── 🌐 URL do Google Sheets
├── 🏪 Nome da loja (ex: "MDO Londrina")
└── ⚙️ Configurações opcionais
```

### **ETAPA 2: 🔍 EXTRAÇÃO DOS DADOS**
```
📊 Sistema extrai automaticamente:
├── 📋 NPS D+1 (Atendimento)
│   └── Colunas: ID, Data, Nome, Telefone, Avaliação, Vendedor, Loja
├── 🛍️ NPS D+30 (Produto) 
│   └── Colunas: ID, Data, Nome, WhatsApp, Avaliação, Vendedor, Loja
└── ⚠️ NPS Ruim (Casos Críticos)
    └── Colunas: ID, Data, Nome, Telefone, Avaliação, Situação, Resolução
```

### **ETAPA 3: 🧹 PADRONIZAÇÃO**
```
🔧 Sistema automaticamente:
├── ✅ Corrige encoding (avaliaãão → avaliacao)
├── ✅ Padroniza nomes das colunas
├── ✅ Remove dados inválidos
├── ✅ Converte avaliações para números
└── ✅ Organiza dados por tipo de aba
```

### **ETAPA 4: 📊 CÁLCULO DE MÉTRICAS**
```
🧮 Para cada aba calcula:
├── 🟢 Promotores (nota 9-10): % e quantidade
├── 🟡 Neutros (nota 7-8): % e quantidade  
├── 🔴 Detratores (nota ≤6): % e quantidade
├── 📈 Score NPS: (Promotores - Detratores) / Total × 100
└── ⭐ Nota média: Média aritmética das avaliações
```

### **ETAPA 5: 🤖 ANÁLISE IA**
```
🧠 IA (GPT-4o) analisa e gera:
├── 🎯 Insights principais (3-5 pontos estratégicos)
├── 📊 Análise comparativa (D+1 vs D+30)
├── ⚠️ Pontos de atenção (problemas identificados)
├── 🚀 Recomendações estratégicas (3 ações práticas)
└── 👥 Análise de vendedores (top performers)
```

### **ETAPA 6: 📄 GERAÇÃO DE RELATÓRIO**
```
📋 Sistema produz:
├── 📊 Relatório estruturado em texto
│   ├── Cabeçalho com nome da loja e data
│   ├── Métricas NPS detalhadas
│   ├── Casos críticos (se houver NPS Ruim)
│   ├── Insights IA completos
│   └── Resumo geral
├── 💾 Arquivo TXT para backup
└── 📄 PDF customizado com visual da marca
```

### **ETAPA 7: 📤 ENTREGA DOS RESULTADOS**
```
📦 Usuário recebe:
├── 🖥️ CLI: Exibe no terminal + salva arquivos
├── 🌐 WEB: Mostra na tela + download PDF
├── 📁 Arquivos salvos em /relatorios/
└── 📊 Estatísticas da análise
```

---

## 🏗️ **ARQUITETURA TÉCNICA COMPLETA**

### **🧠 COMPONENTES PRINCIPAIS**

#### **1. 📥 EXTRAÇÃO (analisador_nps_completo.py)**
```python
🔧 Função: Conectar com Google Sheets e extrair dados
📊 Responsabilidades:
├── Identificar ID da planilha
├── Testar múltiplos GIDs (0, 1, 2, 476804694, 1410159651...)
├── Detectar tipo de aba por colunas e conteúdo
├── Corrigir problemas de encoding
└── Padronizar estrutura dos dados
```

#### **2. 🧮 CÁLCULOS (interno ao analisador)**
```python
🔧 Função: Processar dados e calcular métricas NPS
📊 Responsabilidades:
├── Validar dados (range 0-10)
├── Classificar em Promotores/Neutros/Detratores
├── Calcular Score NPS por aba
├── Gerar estatísticas de vendedores
└── Identificar casos críticos
```

#### **3. 🤖 IA ANÁLISE (OpenAI GPT-4o)**
```python
🔧 Função: Gerar insights estratégicos inteligentes
📊 Responsabilidades:
├── Analisar padrões nos dados
├── Comparar performance D+1 vs D+30
├── Identificar problemas e oportunidades
├── Sugerir ações práticas
└── Gerar relatório em linguagem natural
```

#### **4. 📄 GERAÇÃO PDF (gerador_pdf.py)**
```python
🔧 Função: Criar PDF com visual customizado
📊 Responsabilidades:
├── Aplicar marca "Mercadão dos Óculos"
├── Formatar texto com HTML/CSS
├── Adicionar gráficos e tabelas
├── Gerar arquivo PDF final
└── Salvar em diretório de relatórios
```

---

## 🗃️ **ESTRUTURA DE DADOS PROCESSADOS**

### **📊 FORMATO INTERNO DOS DADOS**
```python
dados_segmentados = {
    'atendimento': DataFrame,  # D+1 data
    'produto': DataFrame,      # D+30 data  
    'nps_ruim': DataFrame,     # Critical cases
    'todos': DataFrame         # Combined data
}

# Cada DataFrame contém:
colunas_padronizadas = [
    'data', 'nome_completo', 'primeiro_nome',
    'telefone/whatsapp', 'avaliacao', 'comentario',
    'vendedor', 'loja', 'tipo_aba'
]
```

### **📈 MÉTRICAS CALCULADAS**
```python
metricas_nps = {
    'tipo': 'Atendimento/Produto',
    'total_respostas': int,
    'promotores': {'count': int, 'percentual': float},
    'neutros': {'count': int, 'percentual': float}, 
    'detratores': {'count': int, 'percentual': float},
    'nps_score': float,
    'nota_media': float
}
```

---

## 🚀 **INTERFACES DO SISTEMA**

### **🖥️ INTERFACE CLI (main.py)**
```
🎯 MENU PRINCIPAL:
┌─────────────────────────────────────────┐
│ 1. 📋 Gerar Relatório Completo         │
│ 2. 🔍 Testar Extração                  │
│ 3. 📄 Instruções                       │
│ 4. 🔧 Configurar Autenticação          │ 
│ 5. 🚪 Sair                             │
└─────────────────────────────────────────┘
```

### **🌐 INTERFACE WEB (frontend/)**
```
📱 PÁGINA WEB:
┌─────────────────────────────────────────┐
│ 🎯 ANÁLISE NPS - MERCADÃO DOS ÓCULOS   │
│                                         │
│ 📎 URL da Planilha: [_______________]   │
│ 🏪 Nome da Loja:   [_______________]   │
│                                         │
│ [ 🚀 GERAR RELATÓRIO ]                 │
│                                         │
│ 📊 Resultados aparecem aqui...         │
└─────────────────────────────────────────┘
```

---

## 🔄 **FLUXO DE DADOS DETALHADO**

### **📥 INPUT → PROCESSAMENTO → OUTPUT**
```mermaid
🌐 URL Planilha
    ↓
📊 Extração GIDs (0, 1410159651, 476804694...)
    ↓
🔍 Identificação Abas (por colunas + conteúdo)
    ↓
🧹 Padronização (encoding + colunas)
    ↓
🧮 Cálculo Métricas (NPS + estatísticas)
    ↓
🤖 Análise IA (GPT-4o insights)
    ↓
📋 Formatação Relatório (texto estruturado)
    ↓
📄 Geração PDF (visual customizado)
    ↓
📤 Entrega Arquivos (TXT + PDF)
```

---

## ⚙️ **CONFIGURAÇÕES E DEPENDÊNCIAS**

### **🔧 VARIÁVEIS DE AMBIENTE**
```python
# IA Configuration
OPENAI_API_KEY = "sk-proj-SBYkz..." 
OPENAI_MODEL = "gpt-4o"

# Sistema Configuration  
NOME_LOJA_PADRAO = "Mercadão dos Óculos"
DIRETORIO_RELATORIOS = "./relatorios/"
PORTA_WEB = 8080
```

### **📦 DEPENDÊNCIAS PRINCIPAIS**
```python
# Processamento de dados
pandas >= 1.3.0
requests >= 2.25.0

# IA e análise
openai >= 1.0.0

# Geração PDF
weasyprint >= 55.0

# Interface web
flask >= 2.0.0
flask-cors >= 3.0.0
```

---

## 🛠️ **LOGS E DEBUG**

### **📊 SAÍDAS DO SISTEMA**
```
🔍 Conectando com: https://docs.google.com/spreadsheets/...
✅ NPS_D1: 4457 registros (GID 0)
✅ NPS_D30: 4597 registros (GID 1410159651)  
✅ NPS_Ruim: 140 registros (GID 476804694)
🤖 Gerando insights com IA...
✅ Relatório gerado: relatorio_MDO_20250727_140028.pdf
```

### **⚠️ TRATAMENTO DE ERROS**
```python
# Principais situações tratadas:
├── URL inválida ou planilha inacessível
├── Abas não encontradas (continua com disponíveis)
├── Problemas de encoding (correção automática)
├── Dados inválidos (filtro automático)
├── Falha na IA (relatório básico como fallback)
└── Erro na geração PDF (mantém TXT)
```

---

## 🎯 **OUTPUTS FINAIS**

### **📄 RELATÓRIO GERADO**
```
╔═══════════════════════════════════════════════════════════════╗
║                    RELATÓRIO NPS COMPLETO                    ║
║                   MERCADÃO DOS ÓCULOS                           ║
╚═══════════════════════════════════════════════════════════════╝

📅 Data da Análise: 27/07/2025 às 14:00

🎯 ATENDIMENTO:
   📊 Total de Respostas: 2,670
   📈 Score NPS: 92.9
   ⭐ Nota Média: 9.75

🎯 PRODUTO:
   📊 Total de Respostas: 1,451  
   📈 Score NPS: 80.5
   ⭐ Nota Média: 9.38

📊 CASOS CRÍTICOS: 140 casos analisados

🤖 INSIGHTS IA:
   • Performance excepcional no atendimento
   • Oportunidades de melhoria no produto
   • Recomendações estratégicas específicas
```

### **💾 ARQUIVOS SALVOS**
```
📁 /relatorios/
├── 📄 relatorio_MDO_Londrina_20250727_140028.pdf
└── 📝 relatorio_MDO_Londrina_20250727_140028.txt
```

---

## 🎮 **COMO USAR O SISTEMA COMPLETO**

### **🖥️ MODO CLI:**
```bash
cd /home/leonardo/DashBot/nps_automation
source nps_env/bin/activate
python3 main.py
# Escolha opção 1, forneça URL e nome da loja
```

### **🌐 MODO WEB:**
```bash
cd /home/leonardo/DashBot/nps_automation/frontend  
python3 server.py
# Abra http://localhost:8080
# Cole URL da planilha e clique "Gerar Relatório"
```

---

**🎯 SISTEMA COMPLETO MAPEADO - PRONTO PARA INTEGRAÇÃO!**