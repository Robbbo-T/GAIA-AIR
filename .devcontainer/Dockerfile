# Usa una imagen base
FROM mcr.microsoft.com/devcontainers/universal:2

# Instala Node.js
RUN apt-get update && apt-get install -y nodejs npm

# Instala Python
RUN apt-get install -y python3 python3-pip

# Instala otras dependencias necesarias
RUN pip3 install --upgrade pip
