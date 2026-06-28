# ============================================================================
# Legado Eterno — Frontend (React/Vite) — multi-stage
# ============================================================================

# --- Dependencias ------------------------------------------------------------
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# --- Desarrollo --------------------------------------------------------------
FROM node:22-alpine AS development
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# --- Build de producción -----------------------------------------------------
FROM node:22-alpine AS build
WORKDIR /app
ARG VITE_API_BASE_URL
ARG VITE_PUBLIC_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_PUBLIC_BASE_URL=$VITE_PUBLIC_BASE_URL
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# --- Servidor estático -------------------------------------------------------
FROM nginx:1.27-alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
