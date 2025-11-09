FROM node:22-alpine as builder

WORKDIR /app

# Copiar package files
COPY package*.json ./
COPY pnpm-lock.yaml* ./

# Instalar dependências
RUN npm install -g pnpm && pnpm install

# Copiar código
COPY . .

# Build
RUN pnpm run build

# Serve stage
FROM node:22-alpine

WORKDIR /app

# Instalar serve para servir a aplicação
RUN npm install -g serve

# Copiar build do estágio anterior
COPY --from=builder /app/dist ./dist

# Expor porta
EXPOSE 3000

# Comando para iniciar
CMD ["serve", "-s", "dist", "-l", "3000"]
