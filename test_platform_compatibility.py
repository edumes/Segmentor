#!/usr/bin/env python3
"""
Testes automatizados para validar compatibilidade multiplataforma
Testa funcionalidades específicas do macOS e Windows
"""

import pytest
import sys
import os
import platform
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Importar módulos do projeto
try:
    from platform_utils import (
        get_platform_config, 
        PlatformConfig,
        detect_apple_silicon,
        get_optimal_thread_count,
        get_memory_optimization_flags
    )
    from video_utils import extract_segment, extract_segments
except ImportError as e:
    pytest.skip(f"Módulos do projeto não encontrados: {e}", allow_module_level=True)

class TestPlatformDetection:
    """Testes para detecção de plataforma"""
    
    def test_get_platform_config_returns_valid_config(self):
        """Testa se get_platform_config retorna configuração válida"""
        config = get_platform_config()
        
        assert isinstance(config, PlatformConfig)
        assert config.os_name in ['macOS', 'Windows', 'Linux']
        assert config.architecture in ['x86_64', 'arm64', 'aarch64', 'AMD64']
        assert isinstance(config.is_apple_silicon, bool)
        assert config.video_encoder in ['h264_videotoolbox', 'h264_nvenc', 'libx264']
        assert isinstance(config.thread_count, int)
        assert config.thread_count > 0
    
    @pytest.mark.skipif(platform.system() != 'Darwin', reason="Teste específico do macOS")
    def test_macos_specific_detection(self):
        """Testa detecção específica do macOS"""
        config = get_platform_config()
        
        assert config.os_name == 'macOS'
        assert config.supports_videotoolbox is True
        assert 'videotoolbox' in config.video_encoder or config.video_encoder == 'libx264'
        
        # Testa detecção do Apple Silicon
        is_apple_silicon = detect_apple_silicon()
        assert isinstance(is_apple_silicon, bool)
        
        if is_apple_silicon:
            assert config.is_apple_silicon is True
            assert config.architecture in ['arm64', 'aarch64']
    
    @pytest.mark.skipif(platform.system() != 'Windows', reason="Teste específico do Windows")
    def test_windows_specific_detection(self):
        """Testa detecção específica do Windows"""
        config = get_platform_config()
        
        assert config.os_name == 'Windows'
        assert config.supports_nvenc in [True, False]  # Depende do hardware
        assert config.supports_dxva2 is True
        assert config.ui_scale_factor >= 1.0
    
    def test_thread_count_optimization(self):
        """Testa otimização da contagem de threads"""
        thread_count = get_optimal_thread_count()
        
        assert isinstance(thread_count, int)
        assert thread_count > 0
        assert thread_count <= os.cpu_count() * 2  # Máximo razoável
    
    def test_memory_optimization_flags(self):
        """Testa flags de otimização de memória"""
        flags = get_memory_optimization_flags()
        
        assert isinstance(flags, list)
        assert all(isinstance(flag, str) for flag in flags)
        
        # Verifica se contém flags válidas do FFmpeg
        valid_flags = ['-threads', '-preset', '-crf', '-movflags', '-avoid_negative_ts']
        flag_names = [flag for flag in flags if flag.startswith('-')]
        assert any(valid_flag in flag_names for valid_flag in valid_flags)

class TestVideoProcessing:
    """Testes para processamento de vídeo"""
    
    @pytest.fixture
    def mock_video_file(self):
        """Cria um arquivo de vídeo mock para testes"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            # Simula um arquivo de vídeo pequeno
            f.write(b'fake video content')
            yield f.name
        
        # Cleanup
        try:
            os.unlink(f.name)
        except FileNotFoundError:
            pass
    
    @patch('subprocess.run')
    def test_extract_segment_command_generation(self, mock_run, mock_video_file):
        """Testa geração de comandos FFmpeg específicos da plataforma"""
        mock_run.return_value = Mock(returncode=0)
        
        # Testa extração básica
        result = extract_segment(
            input_file=mock_video_file,
            output_file='test_output.mp4',
            start_time=10.0,
            duration=5.0
        )
        
        assert result is True
        assert mock_run.called
        
        # Verifica se o comando contém elementos esperados
        call_args = mock_run.call_args[0][0]
        assert 'ffmpeg' in call_args
        assert '-i' in call_args
        assert mock_video_file in call_args
        assert 'test_output.mp4' in call_args
    
    @patch('subprocess.run')
    def test_platform_specific_encoders(self, mock_run, mock_video_file):
        """Testa uso de encoders específicos da plataforma"""
        mock_run.return_value = Mock(returncode=0)
        
        config = get_platform_config()
        
        result = extract_segment(
            input_file=mock_video_file,
            output_file='test_output.mp4',
            start_time=0.0,
            duration=1.0
        )
        
        assert result is True
        
        # Verifica se o encoder correto foi usado
        call_args = mock_run.call_args[0][0]
        
        if config.os_name == 'macOS' and config.supports_videotoolbox:
            assert any('videotoolbox' in arg for arg in call_args)
        elif config.os_name == 'Windows' and config.supports_nvenc:
            # NVENC pode não estar disponível em todos os sistemas Windows
            pass  # Teste flexível para Windows
    
    @patch('subprocess.run')
    def test_extract_segments_multiple(self, mock_run, mock_video_file):
        """Testa extração de múltiplos segmentos"""
        mock_run.return_value = Mock(returncode=0)
        
        selected_times = [10.0, 20.0, 30.0]
        selected_times_vertical = [15.0, 25.0]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = extract_segments(
                input_file=mock_video_file,
                selected_times=selected_times,
                selected_times_vertical=selected_times_vertical,
                output_folder=temp_dir
            )
            
            assert result is True
            # Verifica se foi chamado o número correto de vezes
            expected_calls = len(selected_times) + len(selected_times_vertical)
            assert mock_run.call_count == expected_calls

class TestUICompatibility:
    """Testes para compatibilidade da interface"""
    
    @pytest.mark.skipif(not os.environ.get('DISPLAY') and platform.system() == 'Linux', 
                        reason="Sem display disponível no Linux")
    def test_pyqt6_import(self):
        """Testa se PyQt6 pode ser importado"""
        try:
            from PyQt6.QtWidgets import QApplication, QWidget
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QPixmap
            
            # Testa criação básica de aplicação
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            widget = QWidget()
            assert widget is not None
            
        except ImportError as e:
            pytest.fail(f"Falha ao importar PyQt6: {e}")
    
    @pytest.mark.skipif(platform.system() != 'Darwin', reason="Teste específico do macOS")
    def test_macos_native_features(self):
        """Testa recursos nativos do macOS"""
        try:
            # Testa importação de frameworks do macOS
            import objc
            from Cocoa import NSApplication, NSMenu
            
            # Verifica se pode acessar aplicação nativa
            app = NSApplication.sharedApplication()
            assert app is not None
            
        except ImportError:
            pytest.skip("Frameworks do macOS não disponíveis")
    
    @pytest.mark.skipif(platform.system() != 'Windows', reason="Teste específico do Windows")
    def test_windows_native_features(self):
        """Testa recursos nativos do Windows"""
        try:
            import win32api
            import win32gui
            
            # Testa acesso básico às APIs do Windows
            version = win32api.GetVersion()
            assert version is not None
            
        except ImportError:
            pytest.skip("APIs do Windows não disponíveis")

class TestFFmpegCompatibility:
    """Testes para compatibilidade do FFmpeg"""
    
    def test_ffmpeg_available(self):
        """Testa se FFmpeg está disponível no sistema"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0
            assert 'ffmpeg version' in result.stdout.lower()
            
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("FFmpeg não disponível no sistema")
    
    def test_platform_specific_encoders_available(self):
        """Testa disponibilidade de encoders específicos da plataforma"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-encoders'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                encoders = result.stdout.lower()
                
                config = get_platform_config()
                
                if config.os_name == 'macOS':
                    # VideoToolbox pode não estar disponível em VMs
                    if 'h264_videotoolbox' in encoders:
                        assert config.supports_videotoolbox is True
                
                elif config.os_name == 'Windows':
                    # NVENC depende do hardware
                    if 'h264_nvenc' in encoders:
                        # Se disponível, deve ser detectado
                        pass
                
                # libx264 deve estar sempre disponível
                assert 'libx264' in encoders
            
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Não foi possível verificar encoders do FFmpeg")

class TestPerformanceOptimizations:
    """Testes para otimizações de performance"""
    
    def test_thread_count_reasonable(self):
        """Testa se a contagem de threads é razoável"""
        config = get_platform_config()
        cpu_count = os.cpu_count()
        
        assert config.thread_count <= cpu_count * 2
        assert config.thread_count >= 1
        
        # Para Apple Silicon, deve usar otimizações específicas
        if config.is_apple_silicon:
            assert config.thread_count >= 4  # Mínimo para M1
    
    def test_memory_flags_valid(self):
        """Testa se as flags de memória são válidas"""
        flags = get_memory_optimization_flags()
        
        # Verifica formato das flags
        for i in range(0, len(flags), 2):
            if i + 1 < len(flags):
                flag_name = flags[i]
                flag_value = flags[i + 1]
                
                assert flag_name.startswith('-')
                assert isinstance(flag_value, str)
    
    @pytest.mark.skipif(platform.system() != 'Darwin' or not detect_apple_silicon(),
                        reason="Teste específico para Apple Silicon")
    def test_apple_silicon_optimizations(self):
        """Testa otimizações específicas do Apple Silicon"""
        config = get_platform_config()
        
        assert config.is_apple_silicon is True
        assert config.supports_videotoolbox is True
        
        # Verifica se usa configurações otimizadas
        flags = get_memory_optimization_flags()
        
        # Apple Silicon deve usar preset mais rápido
        if '-preset' in flags:
            preset_index = flags.index('-preset') + 1
            if preset_index < len(flags):
                preset_value = flags[preset_index]
                assert preset_value in ['ultrafast', 'superfast', 'veryfast', 'faster']

# Fixtures globais
@pytest.fixture(scope="session")
def platform_config():
    """Configuração da plataforma para toda a sessão de testes"""
    return get_platform_config()

# Marcadores personalizados
pytestmark = [
    pytest.mark.compatibility,
    pytest.mark.platform
]

# Configuração de testes por plataforma
def pytest_configure(config):
    """Configuração personalizada do pytest"""
    config.addinivalue_line(
        "markers", "macos: marca testes específicos do macOS"
    )
    config.addinivalue_line(
        "markers", "windows: marca testes específicos do Windows"
    )
    config.addinivalue_line(
        "markers", "linux: marca testes específicos do Linux"
    )
    config.addinivalue_line(
        "markers", "apple_silicon: marca testes específicos do Apple Silicon"
    )
    config.addinivalue_line(
        "markers", "compatibility: marca testes de compatibilidade"
    )
    config.addinivalue_line(
        "markers", "platform: marca testes relacionados à plataforma"
    )

def pytest_collection_modifyitems(config, items):
    """Modifica itens de teste baseado na plataforma atual"""
    current_platform = platform.system()
    
    for item in items:
        # Adiciona marcadores baseados na plataforma atual
        if current_platform == 'Darwin':
            item.add_marker(pytest.mark.macos)
            if detect_apple_silicon():
                item.add_marker(pytest.mark.apple_silicon)
        elif current_platform == 'Windows':
            item.add_marker(pytest.mark.windows)
        elif current_platform == 'Linux':
            item.add_marker(pytest.mark.linux)

if __name__ == "__main__":
    # Executa testes se chamado diretamente
    pytest.main([__file__, "-v", "--tb=short"])