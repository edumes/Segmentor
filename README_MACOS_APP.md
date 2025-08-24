# Segmentor - Aplicativo macOS

## 📱 Sobre o Aplicativo

O Segmentor é um aplicativo nativo para macOS que permite segmentar vídeos de forma intuitiva e eficiente. Este executável foi criado especificamente para funcionar de forma independente, sem necessidade de instalação de Python ou outras dependências.

## 🎯 Características

- **Aplicativo nativo .app** - Funciona como qualquer aplicativo macOS
- **Interface moderna** - Desenvolvido com PyQt6 para uma experiência nativa
- **Otimizado para Apple Silicon** - Suporte completo para processadores M1/M2/M3
- **Sem dependências externas** - Todos os recursos incluídos no pacote
- **Suporte a múltiplos formatos** - MP4, MOV, AVI e outros formatos de vídeo
- **Aceleração de hardware** - Utiliza VideoToolbox no macOS para melhor performance

## 📋 Requisitos do Sistema

- **macOS 10.15 (Catalina)** ou superior
- **Arquitetura**: Intel x64 ou Apple Silicon (M1/M2/M3)
- **Espaço em disco**: ~200MB para o aplicativo
- **Memória RAM**: 4GB recomendado

## 🚀 Instalação

### Método 1: Download Direto

1. Baixe o arquivo `Segmentor.app` da pasta `dist/`
2. Arraste o aplicativo para a pasta **Aplicativos** (Applications)
3. Pronto! O aplicativo está instalado

### Método 2: Build Manual

Se você quiser compilar o aplicativo do código fonte:

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd Segmentor

# Instale as dependências
pip install -r requirements.txt

# Execute o script de build
python build_macos.py

# O aplicativo será criado em dist/Segmentor.app
```

## 🔧 Primeira Execução

### Configurações de Segurança

No primeiro uso, o macOS pode exibir um aviso de segurança:

1. **Se aparecer "Não é possível abrir":**
   - Vá em **Preferências do Sistema** > **Segurança e Privacidade**
   - Clique em **Abrir Mesmo Assim** na aba **Geral**

2. **Alternativa via Terminal:**
   ```bash
   xattr -d com.apple.quarantine /Applications/Segmentor.app
   ```

### Permissões

O aplicativo pode solicitar permissões para:
- **Acesso a arquivos**: Para ler vídeos e salvar segmentos
- **Acesso à pasta Downloads**: Para acessar vídeos baixados
- **Acesso à área de trabalho**: Para vídeos na área de trabalho

## 📖 Como Usar

### 1. Abrir Vídeo
- Clique em **"Selecionar Vídeo"** ou
- Arraste e solte um arquivo de vídeo na janela

### 2. Visualizar Segmentos
- O aplicativo mostrará miniaturas dos segmentos de 1 minuto
- Cada miniatura representa um segmento do vídeo

### 3. Selecionar Segmentos
- **Clique** nas miniaturas para selecionar segmentos individuais
- **Selecionar Todos (Padrão)**: Seleciona todos os segmentos horizontais
- **Selecionar Todos (Vertical)**: Seleciona todos os segmentos verticais
- **Limpar Seleção**: Remove todas as seleções

### 4. Extrair Segmentos
- Clique em **"Extrair Segmentos Selecionados"**
- Escolha a pasta de destino
- Aguarde o processamento

## ⚙️ Configurações Avançadas

### Formatos Suportados

**Entrada:**
- MP4, MOV, AVI, MKV, WMV, FLV
- Codecs: H.264, H.265/HEVC, VP9

**Saída:**
- MP4 (H.264) - Padrão
- Otimizado para web e dispositivos móveis

### Otimizações de Performance

O aplicativo detecta automaticamente:
- **Apple Silicon**: Usa aceleração VideoToolbox
- **Intel**: Usa otimizações x64
- **Memória disponível**: Ajusta buffers automaticamente

## 🛠️ Solução de Problemas

### Problemas Comuns

**1. Aplicativo não abre**
```bash
# Verificar permissões
ls -la /Applications/Segmentor.app/Contents/MacOS/Segmentor

# Deve mostrar: -rwxr-xr-x (executável)
```

**2. Erro "Arquivo corrompido"**
```bash
# Remover quarentena
xattr -d com.apple.quarantine /Applications/Segmentor.app
```

**3. Vídeo não carrega**
- Verifique se o formato é suportado
- Tente converter o vídeo para MP4 primeiro
- Verifique se o arquivo não está corrompido

**4. Processamento lento**
- Feche outros aplicativos pesados
- Verifique espaço disponível em disco
- Para vídeos 4K, considere usar resolução menor

### Logs de Debug

Para obter logs detalhados:
```bash
# Executar via terminal para ver logs
/Applications/Segmentor.app/Contents/MacOS/Segmentor
```

## 📁 Estrutura do Aplicativo

```
Segmentor.app/
├── Contents/
│   ├── Info.plist          # Metadados do aplicativo
│   ├── MacOS/
│   │   └── Segmentor       # Executável principal
│   ├── Resources/
│   │   ├── icon.icns       # Ícone do aplicativo
│   │   └── assets/         # Recursos adicionais
│   └── Frameworks/         # Bibliotecas incluídas
│       ├── PyQt6/
│       ├── OpenCV/
│       └── ...
```

## 🔄 Atualizações

Para atualizar o aplicativo:
1. Baixe a nova versão
2. Substitua o arquivo na pasta Aplicativos
3. Suas configurações serão preservadas

## 📞 Suporte

### Informações do Sistema
Para reportar problemas, inclua:
- Versão do macOS
- Modelo do Mac (Intel/Apple Silicon)
- Versão do Segmentor
- Formato e tamanho do vídeo

### Contato
- **Issues**: Use o sistema de issues do repositório
- **Email**: [seu-email@exemplo.com]

## 📄 Licença

Este aplicativo é distribuído sob a licença [especificar licença].

## 🙏 Créditos

- **PyQt6**: Interface gráfica
- **OpenCV**: Processamento de vídeo
- **FFmpeg**: Codificação de vídeo
- **PyInstaller**: Empacotamento do aplicativo

---

**Versão**: 1.0.0  
**Compatibilidade**: macOS 10.15+  
**Arquitetura**: Universal (Intel + Apple Silicon)  
**Tamanho**: ~200MB