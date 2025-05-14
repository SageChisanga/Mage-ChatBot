# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./

# Update npm and install dependencies with specific handling for ajv
RUN npm install -g npm@latest \
    && npm config set fetch-retry-mintimeout 20000 \
    && npm config set fetch-retry-maxtimeout 120000 \
    #&& npm install ajv@6.12.6 ajv-keywords@3.5.2 --legacy-peer-deps \
    && npm install --legacy-peer-deps \
    && npm cache clean --force

# Copy the rest of the application
COPY . .

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/src ./src
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"] 