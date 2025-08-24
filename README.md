# Segmentor - Editor de Vídeo Multiplataforma

![Segmentor Logo](https://img.shields.io/badge/Segmentor-Video%20Editor-blue?style=for-the-badge)

[![macOS](https://img.shields.io/badge/macOS-Compatible-success?logo=apple&logoColor=white)]()
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-Optimized-success?logo=apple&logoColor=white)]()
[![Windows](https://img.shields.io/badge/Windows-Compatible-success?logo=windows&logoColor=white)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)]()
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green?logo=qt&logoColor=white)]()
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Video%20Processing-red?logo=ffmpeg&logoColor=white)]()

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Recursos](#-recursos)
- [Compatibilidade](#-compatibilidade)
- [Instalação](#-instalação)
  - [macOS (Apple Silicon & Intel)](#macos-apple-silicon--intel)
  - [Windows](#windows)
- [Uso](#-uso)
- [Otimizações Específicas](#-otimizações-específicas)
- [Testes](#-testes)
- [Solução de Problemas](#-solução-de-problemas)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

## 🎯 Visão Geral

O **Segmentor** é um editor de vídeo multiplataforma desenvolvido especificamente para garantir máxima compatibilidade com macOS (incluindo otimizações para Apple Silicon) e Windows. O aplicativo oferece uma interface nativa e intuitiva para segmentação e edição de vídeos, com aceleração de hardware específica para cada plataforma.

### ✨ Principais Diferenciais

- **🍎 Integração Nativa macOS**: Menu bar, notificações, drag-and-drop
- **⚡ Otimizado para Apple Silicon**: M1, M2, M3 e M4
- **🚀 Aceleração de Hardware**: VideoToolbox (macOS), NVENC (Windows)
- **🔄 Compatibilidade Cruzada**: Funcionalidade completa em ambas plataformas
- **🎨 Interface Adaptativa**: Tema escuro, suporte a Retina, escalabilidade

## 🚀 Recursos

### Processamento de Vídeo
- ✅ Segmentação precisa de vídeos
- ✅ Suporte a múltiplos formatos (MP4, MOV, AVI, MKV)
- ✅ Aceleração de hardware específica por plataforma
- ✅ Processamento em lote
- ✅ Pré-visualização em tempo real
- ✅ Otimização automática de qualidade

### Interface do Usuário
- ✅ Design nativo para cada plataforma
- ✅ Suporte a displays de alta densidade (Retina)
- ✅ Tema escuro adaptativo
- ✅ Drag-and-drop intuitivo
- ✅ Atalhos de teclado personalizáveis
- ✅ Barra de progresso em tempo real

### Integração do Sistema
- ✅ **macOS**: Menu bar nativo, notificações do sistema, integração com Finder
- ✅ **Windows**: Integração com Explorer, notificações do sistema
- ✅ Suporte a múltiplos monitores
- ✅ Gerenciamento automático de memória

## 🖥️ Compatibilidade

### Sistemas Operacionais Suportados

| Plataforma | Versão Mínima | Recursos Específicos |
|------------|---------------|----------------------|
| **macOS** | 10.15 Catalina | VideoToolbox, Menu Bar Nativo, Notificações |
| **Apple Silicon** | macOS 11.0 Big Sur | Otimizações M1/M2/M3/M4, Performance Nativa |
| **Windows** | Windows 10 | NVENC, DXVA2, Notificações do Sistema |

### Requisitos de Hardware

#### macOS
- **Processador**: Intel Core i5 ou Apple Silicon (M1/M2/M3/M4)
- **Memória**: 8GB RAM (16GB recomendado para Apple Silicon)
- **Armazenamento**: 2GB de espaço livre
- **GPU**: Metal-compatible (para aceleração VideoToolbox)

#### Windows
- **Processador**: Intel Core i5 ou AMD Ryzen 5
- **Memória**: 8GB RAM (16GB recomendado)
- **Armazenamento**: 2GB de espaço livre
- **GPU**: DirectX 11 compatible (NVIDIA para NVENC)

### Dependências
- **Python**: 3.8 ou superior
- **FFmpeg**: 4.4 ou superior (com encoders específicos)
- **PyQt6**: 6.6.0 ou superior
- **OpenCV**: 4.8.0 ou superior

## 📦 Instalação

### Instalação Automática (Recomendada)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/segmentor.git
cd segmentor

# Execute o instalador automático
python install.py
```

O instalador automático:
- 🔍 Detecta sua plataforma automaticamente
- 📦 Instala dependências específicas
- ⚙️ Configura otimizações de hardware
- 🧪 Executa testes de compatibilidade
- 🚀 Cria scripts de lançamento

---

### macOS (Apple Silicon & Intel)

#### Pré-requisitos

1. **Instalar Homebrew** (se não tiver):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Instalar FFmpeg com VideoToolbox**:
   ```bash
   # Para Apple Silicon (M1/M2/M3/M4)
   brew install ffmpeg
   
   # Verificar se VideoToolbox está disponível
   ffmpeg -encoders | grep videotoolbox
   ```

3. **Instalar Python 3.8+**:
   ```bash
   brew install python@3.11
   ```

#### Instalação Manual

```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Atualizar pip
pip install --upgrade pip

# 3. Instalar dependências base
pip install PyQt6>=6.6.0 opencv-python>=4.8.0 numpy>=1.24.0 Pillow>=10.0.0

# 4. Instalar dependências específicas do macOS
pip install pyobjc-framework-Cocoa>=10.0
pip install pyobjc-framework-AVFoundation>=10.0
pip install pyobjc-framework-CoreMedia>=10.0

# 5. Executar aplicação otimizada
python main_optimized.py
```

#### Recursos Específicos do macOS

- **🎯 VideoToolbox**: Aceleração de hardware nativa da Apple
- **📱 Menu Bar**: Integração completa com a barra de menu
- **🔔 Notificações**: Notificações nativas do sistema
- **📂 Drag & Drop**: Suporte completo do Finder
- **🖥️ Retina**: Suporte otimizado para displays de alta densidade

#### Apple Silicon (M1/M2/M3/M4) - Otimizações Específicas

```bash
# Verificar se está rodando nativamente no Apple Silicon
arch
# Deve retornar: arm64

# Verificar otimizações específicas
python -c "from platform_utils import get_platform_config; print(get_platform_config())"
```

**Otimizações Ativas no Apple Silicon:**
- ⚡ **Performance Nativa**: Execução nativa ARM64
- 🧠 **Unified Memory**: Otimização para arquitetura de memória unificada
- 🎥 **VideoToolbox**: Aceleração de hardware específica
- 🔧 **Thread Optimization**: Configuração otimizada para cores de eficiência/performance

---

### Windows

#### Pré-requisitos

1. **Instalar Python 3.8+**:
   - Baixe de [python.org](https://www.python.org/downloads/windows/)
   - ✅ Marque "Add Python to PATH" durante a instalação

2. **Instalar FFmpeg**:
   
   **Opção A - Chocolatey (Recomendado)**:
   ```powershell
   # Instalar Chocolatey (se não tiver)
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   
   # Instalar FFmpeg
   choco install ffmpeg
   ```
   
   **Opção B - Manual**:
   - Baixe de [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
   - Extraia para `C:\ffmpeg`
   - Adicione `C:\ffmpeg\bin` ao PATH do sistema

3. **Verificar NVENC** (opcional, para GPUs NVIDIA):
   ```cmd
   ffmpeg -encoders | findstr nvenc
   ```

#### Instalação Manual

```cmd
# 1. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# 2. Atualizar pip
python -m pip install --upgrade pip

# 3. Instalar dependências base
pip install PyQt6>=6.6.0 opencv-python>=4.8.0 numpy>=1.24.0 Pillow>=10.0.0

# 4. Instalar dependências específicas do Windows
pip install pywin32>=306

# 5. Executar aplicação
python main_optimized.py
```

#### Recursos Específicos do Windows

- **🚀 NVENC**: Aceleração NVIDIA (se disponível)
- **🎯 DXVA2**: Aceleração DirectX
- **📂 Explorer**: Integração com Windows Explorer
- **🔔 Notificações**: Notificações nativas do Windows 10/11
- **🖥️ Multi-DPI**: Suporte a múltiplas escalas de DPI

---

## 🎮 Uso

### Iniciando o Aplicativo

#### macOS
```bash
# Usando script de lançamento
./run_segmentor.sh

# Ou manualmente
source venv/bin/activate
python main_optimized.py
```

#### Windows
```cmd
REM Usando script de lançamento
run_segmentor.bat

REM Ou manualmente
venv\Scripts\activate
python main_optimized.py
```

### Interface Principal

1. **📂 Upload de Vídeo**:
   - Clique em "Upload Video" ou arraste um arquivo
   - Formatos suportados: MP4, MOV, AVI, MKV, WMV

2. **🎬 Pré-visualização**:
   - Miniaturas são geradas automaticamente
   - Clique nas miniaturas para selecionar segmentos
   - Use checkboxes para vídeos verticais

3. **✂️ Extração**:
   - Clique em "Extract Segments"
   - Acompanhe o progresso na barra inferior
   - Arquivos são salvos na pasta `output/`

### Atalhos de Teclado

| Ação | macOS | Windows |
|------|-------|----------|
| Abrir Arquivo | `⌘ + O` | `Ctrl + O` |
| Extrair Segmentos | `⌘ + E` | `Ctrl + E` |
| Tela Cheia | `⌘ + F` | `F11` |
| Sair | `⌘ + Q` | `Alt + F4` |

### Configurações Avançadas

O aplicativo detecta automaticamente as melhores configurações para sua plataforma:

```python
# Verificar configurações atuais
from platform_utils import get_platform_config
config = get_platform_config()
print(f"Encoder: {config.video_encoder}")
print(f"Threads: {config.thread_count}")
print(f"Apple Silicon: {config.is_apple_silicon}")
```

## ⚡ Otimizações Específicas

### Apple Silicon (M1/M2/M3/M4)

```python
# Otimizações automáticas ativas:
- Execução nativa ARM64
- VideoToolbox hardware acceleration
- Unified Memory optimization
- Efficient/Performance cores balancing
- Metal GPU acceleration
- Native Cocoa integration
```

**Configurações Otimizadas:**
- **Threads**: Configuração automática baseada em cores E/P
- **Memória**: Otimização para arquitetura de memória unificada
- **GPU**: Aceleração Metal para processamento de imagem
- **Encoder**: H.264 VideoToolbox com configurações otimizadas

### Windows com NVIDIA

```python
# Otimizações NVENC (se disponível):
- H.264 NVENC hardware encoding
- CUDA acceleration
- DXVA2 hardware decoding
- Multi-threaded processing
```

**Configurações Otimizadas:**
- **Encoder**: H.264 NVENC (se GPU compatível)
- **Decoder**: DXVA2 hardware acceleration
- **Threads**: Configuração baseada em CPU cores
- **Memory**: Otimização para sistemas com GPU dedicada

## 🧪 Testes

### Executar Todos os Testes

```bash
# Testes completos com relatório
python run_tests.py

# Testes específicos
python run_tests.py --type platform    # Detecção de plataforma
python run_tests.py --type video       # Processamento de vídeo
python run_tests.py --type ui          # Interface do usuário
python run_tests.py --type ffmpeg      # Compatibilidade FFmpeg
python run_tests.py --type performance # Otimizações de performance
```

### Testes Manuais

```bash
# Teste de compatibilidade básica
python -c "from platform_utils import get_platform_config; print('✅ Plataforma detectada:', get_platform_config().os_name)"

# Teste de FFmpeg
ffmpeg -version

# Teste de PyQt6
python -c "from PyQt6.QtWidgets import QApplication; print('✅ PyQt6 funcionando')"
```

### Relatórios de Teste

Os testes geram relatórios detalhados em `test_results/`:
- 📊 **HTML Reports**: Relatórios visuais interativos
- 📄 **Text Reports**: Resumos em texto
- 📈 **Coverage Reports**: Cobertura de código
- 🔍 **JSON Data**: Dados estruturados para análise

## 🔧 Solução de Problemas

### Problemas Comuns

#### macOS

**❌ "VideoToolbox encoder not found"**
```bash
# Verificar se FFmpeg foi compilado com VideoToolbox
ffmpeg -encoders | grep videotoolbox

# Se não aparecer, reinstalar FFmpeg
brew uninstall ffmpeg
brew install ffmpeg
```

**❌ "Permission denied" ao executar**
```bash
# Dar permissão de execução
chmod +x run_segmentor.sh

# Verificar permissões do Python
ls -la $(which python3)
```

**❌ Problemas com pyobjc**
```bash
# Reinstalar frameworks do macOS
pip uninstall pyobjc-framework-Cocoa pyobjc-framework-AVFoundation
pip install pyobjc-framework-Cocoa pyobjc-framework-AVFoundation
```

#### Windows

**❌ "FFmpeg not found"**
```cmd
REM Verificar se FFmpeg está no PATH
ffmpeg -version

REM Se não funcionar, adicionar ao PATH:
REM 1. Abrir "Variáveis de Ambiente"
REM 2. Adicionar caminho do FFmpeg ao PATH
REM 3. Reiniciar terminal
```

**❌ "NVENC not available"**
```cmd
REM Verificar GPU NVIDIA
nvidia-smi

REM Verificar drivers atualizados
REM Baixar de: https://www.nvidia.com/drivers/
```

**❌ Problemas com pywin32**
```cmd
REM Reinstalar pywin32
pip uninstall pywin32
pip install pywin32
python venv\Scripts\pywin32_postinstall.py -install
```

### Problemas de Performance

#### Vídeos Grandes (>4K)

```python
# Configurações recomendadas para vídeos 4K+
# Editar platform_utils.py se necessário:

# Para Apple Silicon
if config.is_apple_silicon and video_resolution > (3840, 2160):
    config.thread_count = min(config.thread_count, 8)
    config.memory_limit = "4G"

# Para Windows
if config.os_name == 'Windows' and video_resolution > (3840, 2160):
    config.use_hardware_decoding = True
    config.buffer_size = "32M"
```

#### Memória Insuficiente

```bash
# Monitorar uso de memória durante processamento
# macOS
top -pid $(pgrep -f "python.*main_optimized")

# Windows
tasklist | findstr python
```

### Logs de Debug

```python
# Ativar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Executar com logs
python main_optimized.py --debug
```

### Suporte

Se os problemas persistirem:

1. 📋 **Colete informações do sistema**:
   ```bash
   python -c "from platform_utils import get_platform_config; import json; print(json.dumps(get_platform_config().__dict__, indent=2))"
   ```

2. 🧪 **Execute testes de diagnóstico**:
   ```bash
   python run_tests.py --type platform
   ```

3. 📝 **Crie um issue** com:
   - Sistema operacional e versão
   - Arquitetura (Intel/Apple Silicon/AMD)
   - Logs de erro completos
   - Configuração do sistema

## 🤝 Contribuição

### Configuração do Ambiente de Desenvolvimento

```bash
# 1. Fork e clone o repositório
git clone https://github.com/seu-usuario/segmentor.git
cd segmentor

# 2. Instalar dependências de desenvolvimento
python install.py
# Responder 'y' quando perguntado sobre pacotes de desenvolvimento

# 3. Instalar hooks de pre-commit
pip install pre-commit
pre-commit install

# 4. Executar testes
python run_tests.py
```

### Padrões de Código

```bash
# Formatação automática
black .

# Linting
flake8 .

# Type checking
mypy .

# Testes com cobertura
pytest --cov=. --cov-report=html
```

### Estrutura do Projeto

```
segmentor/
├── main.py                     # Aplicação original
├── main_optimized.py          # Aplicação otimizada multiplataforma
├── platform_utils.py          # Detecção e configuração de plataforma
├── video_utils.py             # Processamento de vídeo
├── install.py                 # Instalador automático
├── run_tests.py              # Runner de testes
├── test_platform_compatibility.py  # Testes de compatibilidade
├── requirements.txt          # Dependências base
├── pytest.ini              # Configuração de testes
├── README.md               # Esta documentação
└── test_results/          # Relatórios de teste
```

### Adicionando Suporte a Nova Plataforma

1. **Editar `platform_utils.py`**:
   ```python
   def detect_new_platform():
       # Implementar detecção
       pass
   
   def get_new_platform_config():
       # Implementar configurações específicas
       pass
   ```

2. **Adicionar testes em `test_platform_compatibility.py`**:
   ```python
   @pytest.mark.new_platform
   def test_new_platform_detection():
       # Implementar testes
       pass
   ```

3. **Atualizar documentação**

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

```
MIT License

Copyright (c) 2024 Segmentor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🎉 Agradecimentos

- **Apple** - Pelas ferramentas de desenvolvimento e documentação do Apple Silicon
- **Microsoft** - Pelo suporte ao desenvolvimento Windows
- **FFmpeg Team** - Pela excelente biblioteca de processamento de vídeo
- **Qt/PyQt** - Pelo framework de interface multiplataforma
- **OpenCV** - Pelas ferramentas de processamento de imagem

---

<div align="center">

**🚀 Desenvolvido com ❤️ para máxima compatibilidade multiplataforma**

[⬆️ Voltar ao topo](#segmentor---editor-de-vídeo-multiplataforma)

</div>