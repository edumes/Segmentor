#!/bin/bash

# Script para criar um arquivo DMG para distribuição do Segmentor
# Este script cria um instalador DMG profissional para macOS

set -e

# Configurações
APP_NAME="Segmentor"
APP_PATH="dist/Segmentor.app"
DMG_NAME="Segmentor-1.0.0-macOS"
DMG_PATH="dist/${DMG_NAME}.dmg"
TEMP_DMG="dist/temp.dmg"
VOLUME_NAME="Segmentor Installer"
SOURCE_FOLDER="dist/dmg_source"

echo "🚀 Criando DMG para distribuição do ${APP_NAME}..."

# Verificar se o aplicativo existe
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Erro: Aplicativo não encontrado em $APP_PATH"
    echo "Execute primeiro: python build_macos.py"
    exit 1
fi

# Criar pasta temporária para o DMG
echo "📁 Preparando estrutura do DMG..."
rm -rf "$SOURCE_FOLDER"
mkdir -p "$SOURCE_FOLDER"

# Copiar aplicativo
cp -R "$APP_PATH" "$SOURCE_FOLDER/"

# Criar link simbólico para Applications
ln -s /Applications "$SOURCE_FOLDER/Applications"

# Copiar documentação
cp README_MACOS_APP.md "$SOURCE_FOLDER/Leia-me.md"

# Criar arquivo de informações
cat > "$SOURCE_FOLDER/Informações.txt" << EOF
Segmentor v1.0.0 para macOS

INSTALAÇÃO:
1. Arraste o Segmentor.app para a pasta Applications
2. Abra o aplicativo pela primeira vez
3. Autorize as permissões de segurança se solicitado

REQUISITOS:
- macOS 10.15 (Catalina) ou superior
- 200MB de espaço livre
- Processador Intel x64 ou Apple Silicon

SUPORTE:
Consulte o arquivo Leia-me.md para instruções detalhadas.

Versão: 1.0.0
Data: $(date '+%d/%m/%Y')
EOF

# Remover DMG anterior se existir
if [ -f "$DMG_PATH" ]; then
    rm "$DMG_PATH"
fi

if [ -f "$TEMP_DMG" ]; then
    rm "$TEMP_DMG"
fi

# Calcular tamanho necessário (em MB)
SOURCE_SIZE=$(du -sm "$SOURCE_FOLDER" | cut -f1)
DMG_SIZE=$((SOURCE_SIZE + 50))  # Adicionar 50MB de margem

echo "📦 Criando DMG temporário (${DMG_SIZE}MB)..."

# Criar DMG temporário
hdiutil create -srcfolder "$SOURCE_FOLDER" \
    -volname "$VOLUME_NAME" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDRW \
    -size ${DMG_SIZE}m \
    "$TEMP_DMG"

# Montar DMG temporário
echo "🔧 Configurando layout do DMG..."
DEVICE=$(hdiutil attach -readwrite -noverify "$TEMP_DMG" | egrep '^/dev/' | sed 1q | awk '{print $1}')
VOLUME_PATH="/Volumes/$VOLUME_NAME"

# Aguardar montagem
sleep 2

# Configurar aparência do Finder (se possível)
if command -v osascript >/dev/null 2>&1; then
    echo "🎨 Configurando aparência..."
    
    osascript << EOF
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 900, 400}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 72
        set background picture of viewOptions to file ".background:background.png"
        
        -- Posicionar ícones
        set position of item "Segmentor.app" of container window to {150, 200}
        set position of item "Applications" of container window to {350, 200}
        
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
EOF
fi

# Desmontar DMG temporário
echo "💾 Finalizando DMG..."
hdiutil detach "$DEVICE"

# Converter para DMG final comprimido
hdiutil convert "$TEMP_DMG" \
    -format UDZO \
    -imagekey zlib-level=9 \
    -o "$DMG_PATH"

# Limpar arquivos temporários
rm "$TEMP_DMG"
rm -rf "$SOURCE_FOLDER"

# Verificar DMG criado
if [ -f "$DMG_PATH" ]; then
    DMG_SIZE_FINAL=$(du -h "$DMG_PATH" | cut -f1)
    echo "✅ DMG criado com sucesso!"
    echo "📁 Arquivo: $DMG_PATH"
    echo "📏 Tamanho: $DMG_SIZE_FINAL"
    echo ""
    echo "🚀 Para distribuir:"
    echo "   1. Teste o DMG: open \"$DMG_PATH\""
    echo "   2. Faça upload para seu servidor/GitHub Releases"
    echo "   3. Compartilhe o link de download"
    echo ""
    echo "💡 Dica: Para assinatura digital, use:"
    echo "   codesign --sign \"Developer ID\" \"$DMG_PATH\""
else
    echo "❌ Erro: Falha ao criar DMG"
    exit 1
fi

echo "🎉 Processo concluído!"