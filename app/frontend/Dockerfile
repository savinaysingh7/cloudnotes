FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Add custom nginx config to proxy API requests
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY . /usr/share/nginx/html

EXPOSE 80
