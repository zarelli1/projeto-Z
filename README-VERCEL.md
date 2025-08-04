# Deploy NPS Automation no Vercel

## Estrutura para Deploy

Seu projeto foi adaptado para deploy no Vercel com as seguintes mudanças:

### Estrutura de Arquivos
```
projeto-Z/
├── api/                          # Serverless functions (Vercel)
│   ├── analyze.py               # Endpoint principal /api/analyze
│   ├── test.py                  # Endpoint de teste /api/test
│   └── health.py                # Health check /api/health
├── frontend/                     # Arquivos estáticos
│   ├── index.html              # Interface web
│   ├── nps-analyzer.js         # JavaScript (adaptado para Vercel)
│   └── styles.css              # Estilos
├── vercel.json                  # Configuração do Vercel
├── requirements.txt             # Dependências Python (simplificadas)
└── .vercelignore               # Arquivos ignorados no deploy
```

### Mudanças Realizadas

1. **Serverless Functions**: Flask convertido para funções serverless na pasta `/api/`
2. **Frontend Adaptado**: JavaScript modificado para detectar ambiente (local vs produção)
3. **Dependências Otimizadas**: Removidas dependências problemáticas no Vercel
4. **Configuração Vercel**: `vercel.json` configurado para roteamento correto

### Como Fazer Deploy

1. **Instale o Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Faça login no Vercel**:
   ```bash
   vercel login
   ```

3. **Configure as variáveis de ambiente**:
   - Acesse seu dashboard do Vercel
   - Vá em Settings > Environment Variables
   - Adicione: `OPENAI_API_KEY` = sua_chave_da_openai

4. **Deploy**:
   ```bash
   cd projeto-Z
   vercel
   ```

5. **Deploy para produção**:
   ```bash
   vercel --prod
   ```

### Endpoints da API

- `/api/health` - Health check
- `/api/test` - Teste de conexão com planilhas
- `/api/analyze` - Análise completa de dados

### Limitações no Vercel

- **Geração de PDFs**: WeasyPrint removido (dependências C++ complexas)
- **Arquivos grandes**: Relatórios não são salvos permanentemente
- **Timeout**: Máximo 10 segundos para serverless functions (Free tier)

### Alternativas para PDFs

Para contornar a limitação de PDF no Vercel, considere:

1. **Usar serviço externo**: Puppeteer, jsPDF, ou API de terceiros
2. **Deploy híbrido**: Vercel para frontend + servidor separado para PDFs
3. **Upgrade Vercel**: Pro tier tem timeout maior (60s)

### Teste Local

Para testar antes do deploy:
```bash
cd projeto-Z
vercel dev
```

Isso simula o ambiente Vercel localmente.