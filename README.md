# 🤖 Sistema de Automação de WhatsApp para Afiliados

Um sistema completo e profissional para automatizar a cópia de anúncios de um grupo de WhatsApp, substituir links por links de afiliado e repostar em múltiplos grupos gerenciados, com gerenciamento inteligente de lotação de grupos.

## ✨ Funcionalidades Principais

### 🔄 Automação de Anúncios
- **Monitoramento contínuo** do grupo de origem
- **Detecção automática** de mensagens com links
- **Substituição inteligente** de links originais por links de afiliado
- **Postagem em massa** em todos os grupos de destino
- **Delays aleatórios** entre postagens para simular comportamento humano

### 📊 Gerenciamento de Grupos
- **Dashboard visual** para gerenciar todos os grupos
- **Rastreamento de capacidade** em tempo real
- **Lotação automática** de grupos
- **Link único de redirecionamento** que alterna grupos automaticamente
- **Histórico de atividades** e logs detalhados

### 🔗 Gerenciamento de Links de Afiliado
- **Mapeamento de domínios** para links de afiliado
- **Substituição automática** de links em mensagens
- **Interface visual** para adicionar/editar links
- **Suporte a múltiplos domínios**

### 📱 Interface Amigável
- **Dashboard responsivo** para desktop e mobile
- **Gerenciamento visual** de grupos com indicadores de status
- **Estatísticas em tempo real** da atividade
- **Página de redirecionamento** automática para novos membros

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - Dashboard de Gerenciamento                           │
│  - Página de Redirecionamento                           │
│  - Estatísticas em Tempo Real                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓ API REST
┌─────────────────────────────────────────────────────────┐
│                Backend (FastAPI)                         │
│  - Gerenciamento de Grupos                             │
│  - Gerenciamento de Links de Afiliado                  │
│  - Processamento de Mensagens                          │
│  - Redirecionamento Inteligente                        │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
    ┌────────┐  ┌────────┐  ┌──────────┐
    │WhatsApp│  │Database│  │Whapi.Cloud│
    │  Bots  │  │ (PostgreSQL)│   API    │
    └────────┘  └────────┘  └──────────┘
```

---

## 🚀 Quick Start

### Com Docker (Recomendado)

```bash
# 1. Clonar/Extrair o projeto
cd whatsapp_automation

# 2. Configurar variáveis de ambiente
cp docker/.env.example docker/.env
nano docker/.env  # Editar com suas informações

# 3. Iniciar os serviços
cd docker
docker-compose up -d

# 4. Acessar
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Manual (Python + Node.js)

```bash
# Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python -c "from database import init_db; init_db()"
uvicorn main:app --reload

# Frontend (em outro terminal)
cd frontend
npm install
npm run dev
```

Para instruções detalhadas, veja [SETUP.md](./SETUP.md)

---

## 📋 Requisitos

### Obrigatório
- **Docker e Docker Compose** (para produção)
- **Conta Whapi.Cloud** com API Key
- **Dois números de WhatsApp** dedicados

### Opcional (desenvolvimento)
- Python 3.11+
- Node.js 22+
- PostgreSQL 15+

---

## 🔧 Configuração

### 1. Whapi.Cloud

1. Crie conta em [whapi.cloud](https://whapi.cloud)
2. Gere uma API Key
3. Conecte seus dois números de WhatsApp
4. Obtenha o ID do grupo de origem

### 2. Variáveis de Ambiente

```env
# Whapi
WHAPI_API_KEY=seu_whapi_api_key
BOT_READER_NUMBER=5511999999999
BOT_POSTER_NUMBER=5511888888888
SOURCE_GROUP_ID=120363123456789@g.us

# Banco de Dados
DB_USER=automation_user
DB_PASSWORD=senha_segura

# Segurança
SECRET_KEY=gere_com_secrets.token_urlsafe(32)
```

### 3. Adicionar Grupos e Links

Acesse o dashboard em `http://seu-dominio.com/dashboard` e:

1. Vá para **Grupos** → **Adicionar Grupo**
2. Preencha os dados do grupo
3. Vá para **Links** → **Adicionar Link**
4. Configure seus links de afiliado

---

## 📖 Documentação

- **[SETUP.md](./SETUP.md)** - Guia completo de instalação
- **[API Docs](http://localhost:8000/docs)** - Documentação interativa da API (Swagger)
- **[Arquitetura](./backend/README.md)** - Detalhes técnicos do backend

---

## 🔗 Link de Redirecionamento Único

O sistema fornece um link que alterna automaticamente entre grupos:

```
http://seu-dominio.com/redirect
```

**Como funciona:**
1. Usuário clica no link
2. Sistema verifica grupos disponíveis
3. Redireciona para o grupo com mais vagas
4. Se todos estiverem cheios, redireciona para o primeiro

---

## 📊 API Endpoints

### Grupos
```
GET    /api/groups              - Listar grupos
POST   /api/groups              - Criar grupo
GET    /api/groups/{id}         - Detalhes do grupo
PUT    /api/groups/{id}         - Atualizar grupo
DELETE /api/groups/{id}         - Deletar grupo
```

### Links de Afiliado
```
GET    /api/affiliate-links      - Listar links
POST   /api/affiliate-links      - Criar link
PUT    /api/affiliate-links/{id} - Atualizar link
DELETE /api/affiliate-links/{id} - Deletar link
```

### Dashboard
```
GET    /api/dashboard/stats              - Estatísticas gerais
GET    /api/dashboard/group-stats/{id}   - Estatísticas do grupo
```

### Redirecionamento
```
GET    /api/redirect            - Obter link de redirecionamento
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Versão |
|-----------|-----------|--------|
| **Backend** | Python + FastAPI | 3.11 / 0.104 |
| **Frontend** | React + Vite | 19 / 5.0 |
| **Database** | PostgreSQL | 15 |
| **API WhatsApp** | Whapi.Cloud | - |
| **Containerização** | Docker | Latest |

---

## 🔒 Segurança

### ⚠️ Aviso Importante

**Este sistema utiliza APIs Não Oficiais do WhatsApp e viola os Termos de Serviço.** Use por sua conta e risco. Há risco de banimento das contas utilizadas.

### Recomendações

1. Use números dedicados (não pessoais)
2. Configure HTTPS em produção
3. Altere todas as senhas padrão
4. Monitore logs regularmente
5. Faça backup do banco de dados
6. Restrinja acesso ao dashboard

---

## 📈 Monitoramento

O sistema fornece:

- **Dashboard em tempo real** com estatísticas
- **Logs de atividade** detalhados
- **Histórico de postagens** e erros
- **Endpoint de saúde** para monitoramento

```bash
# Verificar saúde da API
curl http://localhost:8000/health

# Ver logs em tempo real
docker-compose logs -f backend
```

---

## 🐛 Troubleshooting

### Erro: "Banco de dados não conecta"
```bash
docker-compose restart postgres
docker-compose logs postgres
```

### Erro: "API Key inválida"
1. Verifique se foi copiada corretamente
2. Regenere em whapi.cloud
3. Atualize o arquivo `.env`

### Erro: "Bot não está conectado"
1. Verifique se o número está em whapi.cloud
2. Escaneie o QR Code novamente
3. Reinicie: `docker-compose restart backend`

Para mais ajuda, veja [SETUP.md](./SETUP.md#-troubleshooting)

---

## 📁 Estrutura do Projeto

```
whatsapp_automation/
├── backend/
│   ├── main.py              # Aplicação FastAPI
│   ├── models.py            # Modelos de banco de dados
│   ├── schemas.py           # Schemas Pydantic
│   ├── database.py          # Configuração do banco
│   ├── whapi_client.py      # Cliente Whapi
│   ├── background_tasks.py  # Tarefas em background
│   ├── config.py            # Configurações
│   ├── requirements.txt     # Dependências Python
│   ├── Dockerfile           # Dockerfile do backend
│   └── .env.example         # Exemplo de variáveis
│
├── frontend/
│   ├── client/
│   │   ├── src/
│   │   │   ├── pages/
│   │   │   │   ├── Home.tsx       # Página inicial
│   │   │   │   ├── Dashboard.tsx  # Dashboard
│   │   │   │   └── Redirect.tsx   # Redirecionamento
│   │   │   ├── components/        # Componentes reutilizáveis
│   │   │   └── App.tsx            # Componente raiz
│   │   ├── package.json
│   │   └── vite.config.ts
│   ├── Dockerfile
│   └── .env.example
│
├── docker/
│   ├── docker-compose.yml   # Orquestração de containers
│   ├── .env.example         # Variáveis de ambiente
│   └── nginx.conf           # Configuração Nginx (opcional)
│
├── SETUP.md                 # Guia de instalação
├── README.md                # Este arquivo
└── LICENSE                  # Licença
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto é fornecido como está, apenas para fins educacionais.

---

## ⚠️ Disclaimer

Este sistema é fornecido "como está" sem garantias. O uso de automação no WhatsApp viola os Termos de Serviço. Você é responsável por qualquer consequência, incluindo banimento de contas.

---

## 📞 Suporte

Para problemas ou dúvidas:

1. Verifique [SETUP.md](./SETUP.md)
2. Consulte a [API Docs](http://localhost:8000/docs)
3. Verifique os logs: `docker-compose logs -f`

---

**Desenvolvido com ❤️ para automação de WhatsApp**

Última atualização: Novembro de 2025
