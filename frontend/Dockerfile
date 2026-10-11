# build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# runtime stage: non-root nginx on port 8080
FROM nginxinc/nginx-unprivileged:1.31.7-alpine3.24-slim

ENV BACKEND_URL=http://backend:8000

COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
