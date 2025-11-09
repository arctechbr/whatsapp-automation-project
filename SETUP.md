# Guia de Instalação e Configuração - Sistema de Automação de WhatsApp

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração Inicial](#configuração-inicial)
3. [Instalação com Docker](#instalação-com-docker)
4. [Instalação Manual](#instalação-manual)
5. [Configuração do Whapi.Cloud](#configuração-do-whapiccloud)
6. [Uso do Sistema](#uso-do-sistema)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

### Obrigatório

- **Docker e Docker Compose** (recomendado para produção)
  - [Instalar Docker](https://docs.docker.com/get-docker/)
  - [Instalar Docker Compose](https://docs.docker.com/compose/install/)

- **Conta Whapi.Cloud** (para automação de WhatsApp)
  - [Criar conta em whapi.cloud](https://whapi.cloud)
  - Obter API Key

- **Dois números de WhatsApp dedicados**
  - Um para leitura de anúncios (Bot Reader)
  - Um para postagem em massa (Bot Poster)

### Opcional (para desenvolvimento)

- **Python 3.11+**
- **Node.js 22+**
- **PostgreSQL 15+**

---

## 🚀 Configuração Inicial

### Passo 1: Clonar ou Baixar o Projeto

```bash
# Se usando git
git clone <seu-repositorio> whatsapp_automation
cd whatsapp_automation

# Ou extrair o arquivo ZIP
unzip whatsapp_automation.zip
cd whatsapp_automation
```

### Passo 2: Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp docker/.env.example docker/.env

# Editar o arquivo .env com suas informações
nano docker/.env
# ou
vim docker/.env
```

**Variáveis importantes a configurar:**

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `WHAPI_API_KEY` | Chave de API do Whapi.Cloud | `seu_whapi_api_key_aqui` |
| `BOT_READER_NUMBER` | Número do bot de leitura | `5511999999999` |
| `BOT_POSTER_NUMBER` | Número do bot de postagem | `5511888888888` |
| `SOURCE_GROUP_ID` | ID do grupo de origem | `120363123456789@g.us` |
| `DB_PASSWORD` | Senha do banco de dados | `senha_segura_aqui` |
| `SECRET_KEY` | Chave secreta JWT | Gere com: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

---

## 🐳 Instalação com Docker (Recomendado)

### Passo 1: Iniciar os Serviços

```bash
cd docker

# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### Passo 2: Verificar Status

```bash
# Listar containers
docker-compose ps

# Verificar saúde da API
curl http://localhost:8000/health

# Acessar aplicação
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Docs da API: http://localhost:8000/docs
```

### Passo 3: Inicializar Banco de Dados

```bash
# Conectar ao container do backend
docker-compose exec backend bash

# Dentro do container, executar inicialização
python -c "from database import init_db; init_db()"

# Sair
exit
```

---

## 🔨 Instalação Manual

### Backend (Python/FastAPI)

```bash
# Navegar para a pasta do backend
cd backend

# Criar ambiente virtual
python3.11 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Copiar arquivo de configuração
cp .env.example .env

# Editar .env com suas informações
nano .env

# Inicializar banco de dados
python -c "from database import init_db; init_db()"

# Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React)

```bash
# Navegar para a pasta do frontend
cd frontend

# Instalar dependências
npm install
# ou
pnpm install

# Criar arquivo de configuração
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Iniciar servidor de desenvolvimento
npm run dev
# ou
pnpm dev

# Build para produção
npm run build
# ou
pnpm build
```

---

## 🔑 Configuração do Whapi.Cloud

### Passo 1: Criar Conta

1. Acesse [whapi.cloud](https://whapi.cloud)
2. Crie uma conta
3. Faça login

### Passo 2: Obter API Key

1. Vá para **Settings** > **API Keys**
2. Clique em **Generate New Key**
3. Copie a chave gerada
4. Cole em `WHAPI_API_KEY` no arquivo `.env`

### Passo 3: Conectar Números de WhatsApp

1. Vá para **Devices** > **Add Device**
2. Escaneie o QR Code com o primeiro número (Bot Reader)
3. Repita para o segundo número (Bot Poster)
4. Anote os IDs dos números

### Passo 4: Obter ID do Grupo de Origem

1. No WhatsApp, crie ou selecione o grupo de origem
2. Adicione o Bot Reader a este grupo
3. Use a API Whapi para obter o ID:

```bash
curl -X GET "https://api.whapi.cloud/groups" \
  -H "Authorization: Bearer seu_whapi_api_key_aqui"
```

4. Procure pelo grupo e copie o `id`
5. Cole em `SOURCE_GROUP_ID` no arquivo `.env`

---

## 📱 Uso do Sistema

### Acessar o Dashboard

1. Abra seu navegador
2. Acesse `http://seu-dominio.com/dashboard`
3. Você verá:
   - **Visão Geral:** Estatísticas dos grupos
   - **Grupos:** Gerenciar todos os seus grupos
   - **Links:** Configurar links de afiliado

### Adicionar um Novo Grupo

1. Vá para a aba **Grupos**
2. Clique em **Adicionar Grupo**
3. Preencha:
   - **Nome:** Nome descritivo do grupo
   - **Link de Convite:** Link do WhatsApp (https://chat.whatsapp.com/...)
   - **Capacidade Máxima:** 257 (padrão do WhatsApp)
   - **Número do Bot:** Número responsável por este grupo
4. Clique em **Salvar**

### Adicionar um Link de Afiliado

1. Vá para a aba **Links**
2. Clique em **Adicionar Link**
3. Preencha:
   - **Domínio Base:** Ex: `shopee.com.br`
   - **Link de Afiliado:** Seu link completo com ID de afiliado
   - **Descrição:** Opcional
4. Clique em **Salvar**

### Link de Redirecionamento Único

O sistema fornece um link único que alterna automaticamente entre grupos:

```
http://seu-dominio.com/redirect
```

**Como usar:**

1. Publique este link na sua homepage
2. Quando um usuário clica, é redirecionado para o próximo grupo disponível
3. Se um grupo encher, o sistema automaticamente direciona para o próximo
4. Se um grupo anterior esvaziar, volta a ser usado

---

## 🔄 Como Funciona a Automação

### Fluxo de Processamento

```
1. Bot Reader monitora o grupo de origem
   ↓
2. Detecta nova mensagem com link
   ↓
3. Extrai o link original
   ↓
4. Consulta mapa de links de afiliado
   ↓
5. Substitui link original pelo de afiliado
   ↓
6. Bot Poster envia para todos os grupos de destino
   ↓
7. Sistema registra atividade no banco de dados
```

### Atualização Automática de Lotação

- A cada **1 hora**, o sistema verifica a contagem de membros de cada grupo
- Se um grupo atingir a capacidade máxima, seu status muda para **CHEIO**
- Se um grupo cheio tiver mais de 5 vagas, volta a **DISPONÍVEL**
- O link de redirecionamento sempre aponta para o grupo mais disponível

---

## 🐛 Troubleshooting

### Problema: "Erro de conexão com banco de dados"

**Solução:**

```bash
# Verificar se o PostgreSQL está rodando
docker-compose ps

# Reiniciar o banco de dados
docker-compose restart postgres

# Verificar logs
docker-compose logs postgres
```

### Problema: "API Key inválida"

**Solução:**

1. Verifique se a chave foi copiada corretamente
2. Verifique se não há espaços em branco
3. Regenere a chave em whapi.cloud
4. Atualize o arquivo `.env`

### Problema: "Bot não está conectado"

**Solução:**

1. Verifique se o número está registrado em whapi.cloud
2. Escaneie o QR Code novamente
3. Verifique se o número tem internet ativa
4. Reinicie o container do backend

### Problema: "Mensagens não estão sendo postadas"

**Solução:**

1. Verifique se o Bot Poster é administrador dos grupos
2. Verifique se o Bot Poster está no grupo
3. Verifique os logs: `docker-compose logs backend`
4. Teste com o endpoint de teste: `POST /api/test/send-message`

### Problema: "Grupos não estão sendo lotados corretamente"

**Solução:**

1. Verifique se a contagem de membros está atualizada
2. Teste manualmente: `POST /api/test/update-group-members/{group_id}`
3. Verifique se a capacidade máxima está correta
4. Verifique os logs do sistema

---

## 📊 Endpoints da API

### Grupos

```
GET    /api/groups              - Listar todos os grupos
POST   /api/groups              - Criar novo grupo
GET    /api/groups/{id}         - Obter detalhes do grupo
PUT    /api/groups/{id}         - Atualizar grupo
DELETE /api/groups/{id}         - Deletar grupo
```

### Links de Afiliado

```
GET    /api/affiliate-links      - Listar todos os links
POST   /api/affiliate-links      - Criar novo link
PUT    /api/affiliate-links/{id} - Atualizar link
DELETE /api/affiliate-links/{id} - Deletar link
```

### Dashboard

```
GET    /api/dashboard/stats              - Estatísticas gerais
GET    /api/dashboard/group-stats/{id}   - Estatísticas de um grupo
```

### Redirecionamento

```
GET    /api/redirect            - Obter link de redirecionamento
```

### Testes (apenas desenvolvimento)

```
POST   /api/test/send-message                  - Enviar mensagem de teste
POST   /api/test/update-group-members/{id}    - Atualizar membros manualmente
```

---

## 🔒 Segurança

### Recomendações

1. **Altere todas as senhas padrão**
   - `DB_PASSWORD`
   - `SECRET_KEY`

2. **Use HTTPS em produção**
   - Configure certificado SSL/TLS
   - Use Nginx como reverse proxy

3. **Restrinja acesso ao dashboard**
   - Configure autenticação
   - Use firewall

4. **Monitore logs**
   - Verifique regularmente os logs
   - Configure alertas

5. **Faça backup do banco de dados**
   - Configure backup automático
   - Teste restauração regularmente

---

## 📞 Suporte

Para problemas ou dúvidas:

1. Verifique os logs: `docker-compose logs -f`
2. Consulte a documentação da API: `http://localhost:8000/docs`
3. Verifique o status da API: `http://localhost:8000/health`

---

## 📝 Licença

Este projeto é fornecido como está, apenas para fins educacionais.

**Aviso:** O uso de automação no WhatsApp viola os Termos de Serviço. Use por sua conta e risco.

---

Última atualização: Novembro de 2025
