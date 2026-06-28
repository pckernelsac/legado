# ============================================================================
# Proxy de Legado Eterno para Dokploy.
# La config se HORNEA en la imagen (no se monta por volumen) para que cada
# `Redeploy` reconstruya la imagen con la config actual y recree el contenedor
# automáticamente. Así no hace falta reiniciar nginx a mano tras cada cambio
# (se evita el problema del inode de los bind-mounts).
# ============================================================================
FROM nginx:1.27-alpine

# http{} global (zonas de rate limit, cache, gzip, etc.).
COPY nginx.conf /etc/nginx/nginx.conf
# server{} de Dokploy: ruteo /api -> backend, buckets MinIO, SPA y CSP.
COPY dokploy.conf /etc/nginx/conf.d/default.conf

# Falla el build si la config tiene errores de sintaxis (deploy seguro).
RUN nginx -t

EXPOSE 80
