FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 5173

# Nginx config for single page app routing
RUN sed -i 's/listen       80;/listen       5173;/g' /etc/nginx/conf.d/default.conf && \
    sed -i 's/location \/ {/location \/ {\n        try_files $uri $uri\/ \/index.html;/g' /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
