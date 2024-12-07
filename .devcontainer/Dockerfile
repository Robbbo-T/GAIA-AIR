# Utiliza una imagen base oficial de Node.js
FROM mcr.microsoft.com/vscode/devcontainers/javascript-node:0-14

# Instala herramientas adicionales si es necesario
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*
