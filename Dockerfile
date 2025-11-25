# Stage 1: Build the client
FROM node:18-alpine AS client-builder
WORKDIR /app/client
COPY client/package*.json ./
RUN npm install
COPY client/ ./
RUN npm run build

# Stage 2: Setup the server
FROM node:18-alpine
WORKDIR /app
COPY server/package*.json ./
RUN npm install --production
COPY server/ ./

# Copy built client assets to server's public directory
COPY --from=client-builder /app/client/dist ./public

# Create database directory
RUN mkdir -p database

# Expose port
EXPOSE 3000

# Start server
CMD ["node", "index.js"]
