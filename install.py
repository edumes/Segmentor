#!/usr/bin/env python3
"""
Script de instalação automatizada para Segmentor
Detecta a plataforma e instala dependências específicas
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

class SegmentorInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.is_apple_silicon = self._detect_apple_silicon()
        self.python_executable = sys.executable
        
    def _detect_apple_silicon(self):
        """Detecta se está rodando em Apple Silicon"""
        if self.system != 'darwin':
            return False
        
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'machdep.cpu.brand_string'],
                capture_output=True,
                text=True,
                check=True
            )
            cpu_brand = result.stdout.strip().lower()
            apple_silicon_indicators = ['apple m1', 'apple m2', 'apple m3', 'apple m4']
            return any(indicator in cpu_brand for indicator in apple_silicon_indicators)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self.machine in ['arm64', 'aarch64']
    
    def print_banner(self):
        """Exibe banner de instalação"""
        print("="*60)
        print("    SEGMENTOR - Instalador Multiplataforma")
        print("="*60)
        print(f"Sistema: {self.system.title()}")
        print(f"Arquitetura: {self.machine}")
        if self.system == 'darwin':
            print(f"Apple Silicon: {'Sim' if self.is_apple_silicon else 'Não'}")
        print(f"Python: {sys.version}")
        print("="*60)
        print()
    
    def check_python_version(self):
        """Verifica se a versão do Python é compatível"""
        print("🔍 Verificando versão do Python...")
        
        if sys.version_info < (3, 8):
            print("❌ Erro: Python 3.8 ou superior é necessário")
            print(f"   Versão atual: {sys.version}")
            return False
        
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
        return True
    
    def check_ffmpeg(self):
        """Verifica se FFmpeg está instalado"""
        print("🔍 Verificando FFmpeg...")
        
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ FFmpeg encontrado")
            
            # Verificar encoders específicos da plataforma
            if self.system == 'darwin':
                if 'h264_videotoolbox' in result.stdout:
                    print("✅ VideoToolbox encoder disponível")
                else:
                    print("⚠️  VideoToolbox encoder não encontrado")
            elif self.system == 'windows':
                if 'h264_nvenc' in result.stdout:
                    print("✅ NVENC encoder disponível")
                else:
                    print("⚠️  NVENC encoder não encontrado")
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ FFmpeg não encontrado")
            self.install_ffmpeg_instructions()
            return False
    
    def install_ffmpeg_instructions(self):
        """Fornece instruções para instalar FFmpeg"""
        print("\n📋 Instruções para instalar FFmpeg:")
        
        if self.system == 'darwin':
            print("   macOS:")
            print("   1. Instale Homebrew: https://brew.sh")
            print("   2. Execute: brew install ffmpeg")
            if self.is_apple_silicon:
                print("   3. Para Apple Silicon, use: brew install ffmpeg --with-videotoolbox")
        elif self.system == 'windows':
            print("   Windows:")
            print("   1. Baixe FFmpeg de: https://ffmpeg.org/download.html")
            print("   2. Extraia e adicione ao PATH do sistema")
            print("   3. Ou use Chocolatey: choco install ffmpeg")
        else:
            print("   Linux:")
            print("   Ubuntu/Debian: sudo apt install ffmpeg")
            print("   CentOS/RHEL: sudo yum install ffmpeg")
            print("   Arch: sudo pacman -S ffmpeg")
    
    def create_virtual_environment(self):
        """Cria ambiente virtual se não existir"""
        venv_path = Path("venv")
        
        if venv_path.exists():
            print("✅ Ambiente virtual já existe")
            return True
        
        print("🔧 Criando ambiente virtual...")
        
        try:
            subprocess.run(
                [self.python_executable, '-m', 'venv', 'venv'],
                check=True
            )
            print("✅ Ambiente virtual criado")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao criar ambiente virtual: {e}")
            return False
    
    def get_venv_python(self):
        """Retorna o caminho para o Python do ambiente virtual"""
        if self.system == 'windows':
            return Path("venv") / "Scripts" / "python.exe"
        else:
            return Path("venv") / "bin" / "python"
    
    def install_base_requirements(self):
        """Instala dependências base"""
        print("📦 Instalando dependências base...")
        
        venv_python = self.get_venv_python()
        
        try:
            # Atualizar pip
            subprocess.run(
                [str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'],
                check=True
            )
            
            # Instalar dependências base
            base_packages = [
                'PyQt6>=6.6.0',
                'opencv-python>=4.8.0',
                'numpy>=1.24.0',
                'Pillow>=10.0.0'
            ]
            
            for package in base_packages:
                print(f"   Instalando {package}...")
                subprocess.run(
                    [str(venv_python), '-m', 'pip', 'install', package],
                    check=True
                )
            
            print("✅ Dependências base instaladas")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências base: {e}")
            return False
    
    def install_platform_specific_packages(self):
        """Instala pacotes específicos da plataforma"""
        print(f"🔧 Instalando pacotes específicos para {self.system.title()}...")
        
        venv_python = self.get_venv_python()
        
        try:
            if self.system == 'darwin':
                # Pacotes específicos do macOS
                macos_packages = [
                    'pyobjc-framework-Cocoa>=10.0',
                    'pyobjc-framework-AVFoundation>=10.0',
                    'pyobjc-framework-CoreMedia>=10.0'
                ]
                
                for package in macos_packages:
                    print(f"   Instalando {package}...")
                    try:
                        subprocess.run(
                            [str(venv_python), '-m', 'pip', 'install', package],
                            check=True
                        )
                    except subprocess.CalledProcessError:
                        print(f"   ⚠️  Falha ao instalar {package} (opcional)")
                
            elif self.system == 'windows':
                # Pacotes específicos do Windows
                windows_packages = [
                    'pywin32>=306'
                ]
                
                for package in windows_packages:
                    print(f"   Instalando {package}...")
                    try:
                        subprocess.run(
                            [str(venv_python), '-m', 'pip', 'install', package],
                            check=True
                        )
                    except subprocess.CalledProcessError:
                        print(f"   ⚠️  Falha ao instalar {package} (opcional)")
            
            print("✅ Pacotes específicos da plataforma instalados")
            return True
            
        except Exception as e:
            print(f"⚠️  Alguns pacotes específicos da plataforma falharam: {e}")
            return True  # Não é crítico
    
    def install_development_packages(self):
        """Instala pacotes de desenvolvimento (opcional)"""
        response = input("\n❓ Instalar pacotes de desenvolvimento? (y/N): ")
        
        if response.lower() not in ['y', 'yes', 's', 'sim']:
            return True
        
        print("📦 Instalando pacotes de desenvolvimento...")
        
        venv_python = self.get_venv_python()
        
        dev_packages = [
            'pytest>=7.4.0',
            'pytest-qt>=4.2.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.5.0'
        ]
        
        try:
            for package in dev_packages:
                print(f"   Instalando {package}...")
                subprocess.run(
                    [str(venv_python), '-m', 'pip', 'install', package],
                    check=True
                )
            
            print("✅ Pacotes de desenvolvimento instalados")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar pacotes de desenvolvimento: {e}")
            return False
    
    def create_launch_scripts(self):
        """Cria scripts de lançamento específicos da plataforma"""
        print("🚀 Criando scripts de lançamento...")
        
        try:
            if self.system == 'windows':
                # Script batch para Windows
                batch_content = '''@echo off
cd /d "%~dp0"
call venv\\Scripts\\activate
python main.py
pause
'''
                
                with open('run_segmentor.bat', 'w') as f:
                    f.write(batch_content)
                
                print("✅ Script run_segmentor.bat criado")
                
            else:
                # Script shell para macOS/Linux
                shell_content = '''#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
'''
                
                with open('run_segmentor.sh', 'w') as f:
                    f.write(shell_content)
                
                # Tornar executável
                os.chmod('run_segmentor.sh', 0o755)
                
                print("✅ Script run_segmentor.sh criado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar scripts de lançamento: {e}")
            return False
    
    def test_installation(self):
        """Testa a instalação"""
        print("🧪 Testando instalação...")
        
        venv_python = self.get_venv_python()
        
        test_script = '''
import sys
try:
    import PyQt6
    import cv2
    import numpy
    from platform_utils import get_platform_config
    
    config = get_platform_config()
    print(f"✅ Todos os módulos importados com sucesso")
    print(f"✅ Plataforma detectada: {config.os_name}")
    print(f"✅ Arquitetura: {config.architecture}")
    if config.is_apple_silicon:
        print("✅ Apple Silicon detectado")
    print(f"✅ Encoder de vídeo: {config.video_encoder}")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    sys.exit(1)
'''
        
        try:
            result = subprocess.run(
                [str(venv_python), '-c', test_script],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(result.stdout)
            print("✅ Teste de instalação passou")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Teste de instalação falhou: {e}")
            if e.stdout:
                print(f"Stdout: {e.stdout}")
            if e.stderr:
                print(f"Stderr: {e.stderr}")
            return False
    
    def print_completion_message(self):
        """Exibe mensagem de conclusão"""
        print("\n" + "="*60)
        print("    🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO! 🎉")
        print("="*60)
        print()
        print("📋 Próximos passos:")
        
        if self.system == 'windows':
            print("   1. Execute: run_segmentor.bat")
        else:
            print("   1. Execute: ./run_segmentor.sh")
            print("   2. Ou ative o ambiente: source venv/bin/activate")
            print("   3. E execute: python main.py")
        
        print()
        print("🔧 Recursos específicos da plataforma:")
        
        if self.system == 'darwin':
            print("   ✅ Integração nativa com macOS")
            print("   ✅ Suporte a drag-and-drop")
            print("   ✅ Menu bar nativo")
            print("   ✅ Notificações do sistema")
            if self.is_apple_silicon:
                print("   ✅ Otimizações para Apple Silicon")
                print("   ✅ Aceleração VideoToolbox")
        elif self.system == 'windows':
            print("   ✅ Compatibilidade total com Windows")
            print("   ✅ Suporte a drag-and-drop")
            print("   ✅ Notificações do sistema")
            print("   ✅ Aceleração NVENC (se disponível)")
        
        print()
        print("📚 Documentação: README.md")
        print("🐛 Problemas: Verifique os logs de erro")
        print("="*60)
    
    def run(self):
        """Executa o processo de instalação completo"""
        self.print_banner()
        
        # Verificações preliminares
        if not self.check_python_version():
            return False
        
        if not self.check_ffmpeg():
            print("\n⚠️  FFmpeg é necessário para o funcionamento completo")
            response = input("Continuar mesmo assim? (y/N): ")
            if response.lower() not in ['y', 'yes', 's', 'sim']:
                return False
        
        # Instalação
        steps = [
            self.create_virtual_environment,
            self.install_base_requirements,
            self.install_platform_specific_packages,
            self.install_development_packages,
            self.create_launch_scripts,
            self.test_installation
        ]
        
        for i, step in enumerate(steps, 1):
            print(f"\n[{i}/{len(steps)}] ", end="")
            if not step():
                print(f"\n❌ Instalação falhou na etapa {i}")
                return False
        
        self.print_completion_message()
        return True

def main():
    """Função principal"""
    installer = SegmentorInstaller()
    
    try:
        success = installer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado durante a instalação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()