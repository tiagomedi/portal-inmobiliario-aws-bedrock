# Dockerfile para Frontend HTML/CSS/JS
FROM nginx:alpine

# Copiar archivos estáticos
COPY . /usr/share/nginx/html

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Exponer puerto 80
EXPOSE 80

# Comando por defecto de nginx
CMD ["nginx", "-g", "daemon off;"]
