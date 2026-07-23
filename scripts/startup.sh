#!/bin/bash
# Script de Inicialização do UserBot no Termux
# Copie este arquivo para ~/startup.sh no Termux

echo "🤖 Iniciando Ayugram UserBot..."

# Obter diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Verificar se a pasta existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Pasta do projeto não encontrada!"
    exit 1
fi

# Verificar se o arquivo Python existe
if [ ! -f "$PROJECT_DIR/src/main.py" ]; then
    echo "❌ Arquivo src/main.py não encontrado!"
    exit 1
fi

# Verificar se o .env existe
if [ ! -f "$PROJECT_DIR/config/.env" ]; then
    echo "❌ Arquivo config/.env não encontrado!"
    echo "📝 Configure o arquivo primeiro:"
    echo "   cp config/.env.example config/.env"
    echo "   nano config/.env"
    exit 1
fi

# Mudar para diretório do projeto
cd "$PROJECT_DIR"

# Verificar se já existe uma sessão
if screen -list | grep -q "userbot"; then
    echo "⚠️ Bot já está rodando!"
    echo "📊 Use 'screen -r userbot' para ver"
else
    # Carregar variáveis de ambiente
    export $(cat config/.env | grep -v '^#' | xargs)
    
    # Iniciar o bot em background com screen
    screen -S userbot -d -m python3 src/main.py
    echo "✅ UserBot iniciado em background"
    echo "📊 Use 'screen -r userbot' para ver os logs"
    echo "🔄 Use 'screen -ls' para listar sessões"
fi

# Mostrar status
echo ""
echo "📱 Status:"
ps aux | grep "src/main.py" | grep -v grep || echo "❌ Processo não encontrado"
