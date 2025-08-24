# 📦 Guia de Instalação Detalhado - Segmentor

## 🎯 Visão Geral

Este guia fornece instruções detalhadas para instalação do Segmentor em diferentes plataformas, incluindo solução de problemas específicos e otimizações avançadas.

## 📋 Índice

- [Requisitos do Sistema](#-requisitos-do-sistema)
- [Instalação Automática](#-instalação-automática)
- [Instalação Manual por Plataforma](#-instalação-manual-por-plataforma)
  - [macOS (Apple Silicon)](#-macos-apple-silicon)
  - [macOS (Intel)](#-macos-intel)
  - [Windows 10/11](#-windows-1011)
- [Verificação da Instalação](#-verificação-da-instalação)
- [Configurações Avançadas](#-configurações-avançadas)
- [Solução de Problemas](#-solução-de-problemas)

## 🖥️ Requisitos do Sistema

### Requisitos Mínimos

| Componente | macOS | Windows |
|------------|-------|----------|
| **OS** | macOS 10.15+ | Windows 10+ |
| **CPU** | Intel i5 / Apple M1 | Intel i5 / AMD Ryzen 5 |
| **RAM** | 8GB | 8GB |
| **Storage** | 2GB livre | 2GB livre |
| **Python** | 3.8+ | 3.8+ |

### Requisitos Recomendados

| Componente | macOS | Windows |
|------------|-------|----------|
| **OS** | macOS 12.0+ | Windows 11 |
| **CPU** | Apple M2/M3 | Intel i7 / AMD Ryzen 7 |
| **RAM** | 16GB | 16GB |
| **GPU** | Integrada | NVIDIA GTX 1060+ |
| **Storage** | 5GB livre (SSD) | 5GB livre (SSD) |

## 🚀 Instalação Automática

### Método Recomendado

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/segmentor.git
cd segmentor

# 2. Execute o instalador automático
python install.py
```

### O que o Instalador Faz

1. **🔍 Detecção Automática**:
   - Identifica sistema operacional
   - Detecta arquitetura (Intel/Apple Silicon/AMD)
   - Verifica versão do Python

2. **📦 Instalação de Dependências**:
   - Cria ambiente virtual isolado
   - Instala pacotes base multiplataforma
   - Instala pacotes específicos da plataforma

3. **⚙️ Configuração**:
   - Configura aceleração de hardware
   - Otimiza configurações de performance
   - Cria scripts de lançamento

4. **🧪 Validação**:
   - Executa testes de compatibilidade
   - Verifica funcionamento dos módulos
   - Gera relatório de instalação

---

## 🛠️ Instalação Manual por Plataforma

## 🍎 macOS (Apple Silicon)

### Pré-requisitos

#### 1. Verificar Arquitetura
```bash
# Verificar se está rodando nativamente no Apple Silicon
arch
# Deve retornar: arm64

# Verificar informações do processador
system_profiler SPHardwareDataType | grep "Chip"
```

#### 2. Instalar Xcode Command Line Tools
```bash
xcode-select --install
```

#### 3. Instalar Homebrew (ARM64)
```bash
# Instalar Homebrew nativo para Apple Silicon
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Adicionar ao PATH (se necessário)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Verificar instalação
brew --version
which brew
# Deve mostrar: /opt/homebrew/bin/brew
```

#### 4. Instalar Python 3.11 (ARM64)
```bash
# Instalar Python nativo para Apple Silicon
brew install python@3.11

# Verificar instalação nativa
python3.11 --version
file $(which python3.11)
# Deve mostrar: Mach-O 64-bit executable arm64
```

#### 5. Instalar FFmpeg com VideoToolbox
```bash
# Instalar FFmpeg com suporte completo
brew install ffmpeg

# Verificar encoders disponíveis
ffmpeg -encoders | grep videotoolbox
# Deve mostrar: h264_videotoolbox, hevc_videotoolbox

# Verificar decoders
ffmpeg -decoders | grep videotoolbox
```

### Instalação do Segmentor

```bash
# 1. Navegar para o diretório do projeto
cd segmentor

# 2. Criar ambiente virtual com Python nativo
python3.11 -m venv venv
source venv/bin/activate

# 3. Verificar que está usando Python ARM64
which python
file $(which python)
# Deve mostrar: Mach-O 64-bit executable arm64

# 4. Atualizar pip
pip install --upgrade pip

# 5. Instalar dependências base
pip install PyQt6>=6.6.0
pip install opencv-python>=4.8.0
pip install numpy>=1.24.0
pip install Pillow>=10.0.0

# 6. Instalar frameworks específicos do macOS
pip install pyobjc-framework-Cocoa>=10.0
pip install pyobjc-framework-AVFoundation>=10.0
pip install pyobjc-framework-CoreMedia>=10.0
pip install pyobjc-framework-Quartz>=10.0

# 7. Verificar instalação
python -c "from platform_utils import get_platform_config; config = get_platform_config(); print(f'Apple Silicon: {config.is_apple_silicon}'); print(f'VideoToolbox: {config.supports_videotoolbox}')"
```

### Otimizações Específicas Apple Silicon

```bash
# Configurar variáveis de ambiente para otimização
echo 'export OPENBLAS_NUM_THREADS=1' >> ~/.zprofile
echo 'export MKL_NUM_THREADS=1' >> ~/.zprofile
echo 'export VECLIB_MAXIMUM_THREADS=1' >> ~/.zprofile
echo 'export NUMEXPR_NUM_THREADS=1' >> ~/.zprofile

# Recarregar configurações
source ~/.zprofile
```

---

## 🍎 macOS (Intel)

### Diferenças da Instalação Apple Silicon

#### 1. Homebrew Intel
```bash
# Verificar se está usando Homebrew Intel
which brew
# Deve mostrar: /usr/local/bin/brew (Intel) ou /opt/homebrew/bin/brew (Apple Silicon)

# Se necessário, instalar Homebrew Intel
arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Python Intel
```bash
# Instalar Python Intel
arch -x86_64 brew install python@3.11

# Verificar arquitetura
file $(which python3.11)
# Deve mostrar: Mach-O 64-bit executable x86_64
```

#### 3. Dependências Intel
```bash
# Criar ambiente virtual Intel
arch -x86_64 python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências (mesmo processo que Apple Silicon)
pip install PyQt6>=6.6.0 opencv-python>=4.8.0 numpy>=1.24.0 Pillow>=10.0.0
pip install pyobjc-framework-Cocoa>=10.0
```

---

## 🪟 Windows 10/11

### Pré-requisitos

#### 1. Instalar Python
```powershell
# Opção A: Download direto
# Baixar de: https://www.python.org/downloads/windows/
# ✅ Marcar "Add Python to PATH"
# ✅ Marcar "Install for all users"

# Opção B: Usando winget
winget install Python.Python.3.11

# Verificar instalação
python --version
where python
```

#### 2. Instalar Visual Studio Build Tools
```powershell
# Necessário para compilar algumas dependências
# Baixar de: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Ou usar chocolatey:
choco install visualstudio2022buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools"
```

#### 3. Instalar FFmpeg

**Método A - Chocolatey (Recomendado)**:
```powershell
# Instalar Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar FFmpeg
choco install ffmpeg

# Verificar instalação
ffmpeg -version
```

**Método B - Manual**:
```powershell
# 1. Baixar FFmpeg de: https://www.gyan.dev/ffmpeg/builds/
# 2. Extrair para C:\ffmpeg
# 3. Adicionar C:\ffmpeg\bin ao PATH

# Adicionar ao PATH via PowerShell
$env:PATH += ";C:\ffmpeg\bin"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH, [EnvironmentVariableTarget]::User)
```

#### 4. Verificar GPU NVIDIA (Opcional)
```powershell
# Verificar se há GPU NVIDIA
nvidia-smi

# Verificar suporte NVENC
ffmpeg -encoders | findstr nvenc
```

### Instalação do Segmentor

```cmd
REM 1. Navegar para o diretório do projeto
cd segmentor

REM 2. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

REM 3. Atualizar pip
python -m pip install --upgrade pip

REM 4. Instalar dependências base
pip install PyQt6>=6.6.0
pip install opencv-python>=4.8.0
pip install numpy>=1.24.0
pip install Pillow>=10.0.0

REM 5. Instalar dependências específicas do Windows
pip install pywin32>=306

REM 6. Configurar pywin32
python venv\Scripts\pywin32_postinstall.py -install

REM 7. Verificar instalação
python -c "from platform_utils import get_platform_config; config = get_platform_config(); print(f'Windows: {config.os_name}'); print(f'NVENC: {config.supports_nvenc}')"
```

### Configurações Específicas Windows

#### Configurar Aceleração de Hardware
```cmd
REM Verificar suporte DirectX
dxdiag /t dxdiag_output.txt
type dxdiag_output.txt | findstr "DirectX"

REM Verificar drivers de vídeo atualizados
REM NVIDIA: https://www.nvidia.com/drivers/
REM AMD: https://www.amd.com/support
REM Intel: https://www.intel.com/content/www/us/en/support/
```

---

## ✅ Verificação da Instalação

### Teste Básico de Funcionamento

```bash
# 1. Verificar detecção de plataforma
python -c "from platform_utils import get_platform_config; print(get_platform_config())"

# 2. Verificar PyQt6
python -c "from PyQt6.QtWidgets import QApplication; print('✅ PyQt6 OK')"

# 3. Verificar OpenCV
python -c "import cv2; print(f'✅ OpenCV {cv2.__version__} OK')"

# 4. Verificar FFmpeg
ffmpeg -version | head -1

# 5. Teste de importação completa
python -c "import main_optimized; print('✅ Aplicação OK')"
```

### Executar Testes Automatizados

```bash
# Testes rápidos
python run_tests.py --type platform

# Testes completos
python run_tests.py
```

### Verificar Otimizações Específicas

#### macOS Apple Silicon
```bash
python -c "
from platform_utils import get_platform_config
config = get_platform_config()
print(f'✅ Apple Silicon: {config.is_apple_silicon}')
print(f'✅ VideoToolbox: {config.supports_videotoolbox}')
print(f'✅ Threads: {config.thread_count}')
print(f'✅ Encoder: {config.video_encoder}')
"
```

#### Windows
```cmd
python -c "
from platform_utils import get_platform_config
config = get_platform_config()
print(f'✅ Windows: {config.os_name == "Windows"}')
print(f'✅ NVENC: {config.supports_nvenc}')
print(f'✅ DXVA2: {config.supports_dxva2}')
print(f'✅ Threads: {config.thread_count}')
"
```

---

## ⚙️ Configurações Avançadas

### Otimização de Performance

#### macOS Apple Silicon
```bash
# Criar arquivo de configuração personalizada
cat > ~/.segmentor_config << EOF
[apple_silicon]
max_threads = 8
memory_limit = 4G
use_metal_acceleration = true
videotoolbox_preset = fast
EOF
```

#### Windows com NVIDIA
```cmd
REM Criar arquivo de configuração
echo [nvidia] > %USERPROFILE%\.segmentor_config
echo max_threads = 12 >> %USERPROFILE%\.segmentor_config
echo use_nvenc = true >> %USERPROFILE%\.segmentor_config
echo nvenc_preset = fast >> %USERPROFILE%\.segmentor_config
```

### Configuração de Memória

```python
# Editar platform_utils.py para configurações personalizadas
def get_custom_memory_config():
    import psutil
    total_memory = psutil.virtual_memory().total
    
    if total_memory > 16 * 1024**3:  # 16GB+
        return {
            'buffer_size': '64M',
            'max_memory': '8G',
            'thread_multiplier': 2
        }
    elif total_memory > 8 * 1024**3:  # 8GB+
        return {
            'buffer_size': '32M', 
            'max_memory': '4G',
            'thread_multiplier': 1.5
        }
    else:
        return {
            'buffer_size': '16M',
            'max_memory': '2G', 
            'thread_multiplier': 1
        }
```

---

## 🔧 Solução de Problemas

### Problemas de Instalação

#### Erro: "Python not found"

**macOS**:
```bash
# Verificar instalação do Python
which python3
ls -la /usr/bin/python*

# Reinstalar se necessário
brew reinstall python@3.11
```

**Windows**:
```cmd
REM Verificar instalação
where python
py -0  REM Lista versões instaladas

REM Reinstalar se necessário
winget uninstall Python.Python.3.11
winget install Python.Python.3.11
```

#### Erro: "pip install failed"

```bash
# Limpar cache do pip
pip cache purge

# Atualizar pip
python -m pip install --upgrade pip

# Instalar com verbose para debug
pip install -v PyQt6
```

#### Erro: "FFmpeg not found"

**macOS**:
```bash
# Verificar instalação
which ffmpeg

# Reinstalar
brew uninstall ffmpeg
brew install ffmpeg

# Verificar PATH
echo $PATH | grep -o '/opt/homebrew/bin'
```

**Windows**:
```cmd
REM Verificar PATH
echo %PATH% | findstr ffmpeg

REM Adicionar ao PATH temporariamente
set PATH=%PATH%;C:\ffmpeg\bin

REM Verificar funcionamento
ffmpeg -version
```

### Problemas de Performance

#### Processamento Lento

```python
# Verificar configurações atuais
from platform_utils import get_platform_config
config = get_platform_config()
print(f"Threads: {config.thread_count}")
print(f"Encoder: {config.video_encoder}")
print(f"Hardware Acceleration: {config.supports_videotoolbox or config.supports_nvenc}")

# Monitorar uso de recursos durante processamento
# macOS
# top -pid $(pgrep -f "python.*main_optimized")

# Windows  
# tasklist | findstr python
```

#### Alto Uso de Memória

```bash
# Configurar limite de memória
export SEGMENTOR_MAX_MEMORY=4G

# Ou editar platform_utils.py
# config.memory_limit = "4G"
```

### Problemas de Interface

#### Erro: "QApplication: no such file or directory"

```bash
# Verificar instalação do PyQt6
pip show PyQt6

# Reinstalar se necessário
pip uninstall PyQt6
pip install PyQt6>=6.6.0

# Verificar dependências do sistema
# macOS: Verificar se Xcode Command Line Tools estão instalados
# Windows: Verificar se Visual C++ Redistributable está instalado
```

#### Interface não aparece (Linux/WSL)

```bash
# Configurar display
export DISPLAY=:0

# Ou usar modo offscreen para testes
export QT_QPA_PLATFORM=offscreen
```

### Logs de Debug

```bash
# Executar com logs detalhados
python main_optimized.py --debug --verbose

# Ou configurar logging
export SEGMENTOR_LOG_LEVEL=DEBUG
python main_optimized.py
```

### Coleta de Informações para Suporte

```bash
# Script para coletar informações do sistema
python -c "
import platform
import sys
import subprocess
from platform_utils import get_platform_config

print('=== INFORMAÇÕES DO SISTEMA ===')
print(f'OS: {platform.system()} {platform.release()}')
print(f'Arquitetura: {platform.machine()}')
print(f'Python: {sys.version}')

config = get_platform_config()
print(f'\n=== CONFIGURAÇÃO SEGMENTOR ===')
for key, value in config.__dict__.items():
    print(f'{key}: {value}')

print(f'\n=== FFMPEG ===')
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
    print(result.stdout.split('\n')[0])
except:
    print('FFmpeg não encontrado')
"
```

---

## 📞 Suporte

Se você encontrar problemas não cobertos neste guia:

1. **📋 Execute o script de diagnóstico** (código acima)
2. **🧪 Execute os testes**: `python run_tests.py --type platform`
3. **📝 Crie um issue** no GitHub com:
   - Saída do script de diagnóstico
   - Logs de erro completos
   - Passos para reproduzir o problema
   - Sistema operacional e versão

---

<div align="center">

**🛠️ Guia mantido atualizado para máxima compatibilidade**

[⬆️ Voltar ao README principal](README.md)

</div>