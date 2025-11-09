# Guia de Automação de WhatsApp para Afiliados

## ⚠️ Aviso Importante: Risco de Banimento

Este programa utiliza tecnologias que simulam o comportamento do WhatsApp Web ou APIs Não Oficiais para interagir com o WhatsApp. **O uso dessas ferramentas viola os Termos de Serviço do WhatsApp e acarreta um alto risco de banimento** das contas de telefone utilizadas.

A arquitetura proposta visa mitigar esse risco, separando as funções em números diferentes, mas não o elimina.

---

## 1. Arquitetura da Solução

A solução é dividida em dois módulos principais, operando em um servidor web (VPS ou Cloud) para garantir que a automação funcione 24/7.

### Módulo A: Automação de Anúncios
- **Função Principal:** Copiar, substituir link de afiliado e repostar em grupos
- **Tecnologia Base:** API Não Oficial / Biblioteca de Automação (Ex: `whatsapp-web.js` em Node.js)
- **Risco Associado:** Alto (Leitura e Postagem em Massa)

### Módulo B: Gerenciamento de Lotação
- **Função Principal:** Gerenciar o link de convite único e redirecionar para o grupo disponível
- **Tecnologia Base:** Servidor Web (Ex: Python/Flask ou Node.js/Express) e Banco de Dados
- **Risco Associado:** Baixo (Operação Externa)

---

## 2. Configuração Inicial (Pré-requisitos)

### 2.1. Números de Telefone

Você precisará de, no mínimo, dois números de telefone dedicados:

1. **Número 1 (Bot de Leitura):** Será adicionado ao grupo de origem (o grupo que você monitora).
2. **Número 2 (Bot de Postagem/Gerenciamento):** Será o administrador dos seus grupos de destino e o responsável pela postagem em massa.

### 2.2. Ambiente de Servidor

Recomenda-se um servidor privado virtual (VPS) ou um serviço de hospedagem em nuvem (AWS, Google Cloud, etc.) para rodar o programa continuamente.

### 2.3. Tecnologias Sugeridas

- **Linguagem de Programação:** Python (para o servidor e lógica) e/ou Node.js (para a automação do WhatsApp, se usar `whatsapp-web.js`)
- **Banco de Dados:** SQLite (simples) ou PostgreSQL (escalável)
- **Ferramenta de Automação:** Escolha uma API Não Oficial paga (com suporte a múltiplos números) ou uma biblioteca como `whatsapp-web.js`

---

## 3. Implementação do Módulo A: Automação de Anúncios

Este módulo envolve a configuração do Bot de Leitura (Nº 1) e do Bot de Postagem (Nº 2), e a lógica de processamento.

### Passo 3.1. Configuração do Banco de Dados (Tabelas Essenciais)

Crie as seguintes tabelas no seu banco de dados:

1. **`MAP_LINKS`:** Armazena o mapeamento de links
   - `dominio_base` (TEXT): Ex: `shopee.com.br`
   - `link_afiliado` (TEXT): Seu link de afiliado completo

2. **`GRUPOS_DESTINO`:** Lista dos seus grupos para postagem
   - `id_grupo` (TEXT): ID interno do grupo no WhatsApp
   - `bot_responsavel` (TEXT): O número de telefone do Bot 2

3. **`MENSAGENS_PROCESSADAS`:** Histórico para evitar repetição
   - `id_mensagem` (TEXT): ID único da mensagem lida

### Passo 3.2. Lógica de Substituição de Links

Implemente a função de substituição de links usando **Expressões Regulares (Regex)** para identificar e extrair o link original, e então substituí-lo pelo seu link de afiliado mapeado no DB.

### Passo 3.3. O Loop de Monitoramento e Postagem

1. **Conexão:** Inicie duas instâncias da sua ferramenta de automação (Bot 1 e Bot 2), cada uma conectada ao seu respectivo número de telefone
2. **Leitura (Bot 1):** Configure o Bot 1 para escutar o evento de `nova_mensagem` no grupo de origem
3. **Processamento:** Quando uma mensagem for recebida:
   - Verifique se a mensagem já foi processada
   - Se for nova, extraia o texto e os links
   - Use a lógica de substituição para trocar os links originais pelos seus links de afiliado
   - Registre o ID da mensagem no DB
4. **Postagem (Bot 2):** Use o Bot 2 para enviar a mensagem processada para todos os `id_grupo` listados na tabela `GRUPOS_DESTINO`
   - **Crucial:** Adicione um **intervalo de tempo aleatório** (ex: 5 a 15 segundos) entre as postagens em cada grupo para simular um comportamento humano e reduzir o risco de ser detectado como spam

---

## 4. Implementação do Módulo B: Gerenciamento de Lotação

Este módulo é um sistema de gerenciamento de links de convite.

### Passo 4.1. Configuração do Banco de Dados (Tabela Essencial)

Crie a tabela `GRUPOS_LOTACAO` no seu banco de dados:

- `link_convite` (TEXT): O link de convite do WhatsApp
- `capacidade_maxima` (INTEGER): Ex: 257
- `membros_atuais` (INTEGER): Contagem atual (atualizada pelo Bot 2)
- `status` (TEXT): "DISPONIVEL" ou "CHEIO"
- `ordem` (INTEGER): Ordem de prioridade para lotação

### Passo 4.2. O Servidor de Redirecionamento (Link Único)

Crie um endpoint no seu servidor web (ex: `https://seusite.com/entrar`) que executa a lógica de redirecionamento:

1. **Consulta:** Ao receber uma requisição, consulte a tabela `GRUPOS_LOTACAO` para encontrar o grupo com `status = 'DISPONIVEL'` e a menor `ordem`
2. **Redirecionamento:** Redirecione o usuário para o `link_convite` desse grupo
3. **Plano B:** Se nenhum grupo estiver `DISPONIVEL`, redirecione para uma página de "Lista de Espera" ou para o link de convite do último grupo da lista

### Passo 4.3. Rotina de Atualização de Status

Crie uma rotina agendada (Cron Job) que executa a cada hora:

1. **Contagem de Membros:** O Bot 2 (Cliente de Postagem) deve ser usado para obter a contagem de membros de cada grupo listado em `GRUPOS_LOTACAO`
2. **Atualização:** Atualize o campo `membros_atuais` no DB
3. **Status:** Atualize o campo `status`:
   - Se `membros_atuais` for igual ou maior que `capacidade_maxima`, defina como `CHEIO`
   - Se o grupo estava `CHEIO` e a contagem de membros caiu significativamente (ex: mais de 5 vagas), defina o status de volta para `DISPONIVEL`

---

## 5. Próximos Passos para Você

1. **Escolha da Tecnologia:** Decida qual API Não Oficial ou biblioteca de automação você utilizará
2. **Configuração do Servidor:** Configure seu ambiente de VPS/Cloud com Python/Node.js e o Banco de Dados
3. **Implementação:** Siga a lógica e o pseudocódigo fornecidos para escrever o código real

Este guia fornece o mapa completo para a construção do seu programa de automação.
