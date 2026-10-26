FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.30-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist /usr/share/nginx/html
RUN mkdir -p /tmp/nginx && chown -R nginx:nginx /tmp/nginx /var/cache/nginx /usr/share/nginx/html
USER nginx
EXPOSE 8080
