import platform
import subprocess
import sys
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PlatformConfig:
    """Configuração específica da plataforma"""
    os_name: str
    architecture: str
    is_apple_silicon: bool
    is_macos: bool
    is_windows: bool
    is_linux: bool
    ffmpeg_hwaccel: str
    video_encoder: str
    audio_encoder: str
    thread_count: int
    memory_optimization: Dict[str, Any]
    ui_scaling: float
    native_features: Dict[str, bool]

class PlatformDetector:
    """Detector de plataforma com otimizações específicas para macOS/Apple Silicon"""
    
    def __init__(self):
        self._config: Optional[PlatformConfig] = None
        self._detect_platform()
    
    def _detect_platform(self) -> None:
        """Detecta a plataforma atual e configura otimizações"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Detectar Apple Silicon
        is_apple_silicon = self._is_apple_silicon()
        is_macos = system == 'darwin'
        is_windows = system == 'windows'
        is_linux = system == 'linux'
        
        # Configurar aceleração de hardware baseada na plataforma
        ffmpeg_hwaccel, video_encoder = self._get_hardware_acceleration()
        
        # Configurar número de threads otimizado
        thread_count = self._get_optimal_thread_count()
        
        # Configurar otimizações de memória
        memory_optimization = self._get_memory_optimization()
        
        # Configurar escala de UI
        ui_scaling = self._get_ui_scaling()
        
        # Configurar recursos nativos
        native_features = self._get_native_features()
        
        self._config = PlatformConfig(
            os_name=system,
            architecture=machine,
            is_apple_silicon=is_apple_silicon,
            is_macos=is_macos,
            is_windows=is_windows,
            is_linux=is_linux,
            ffmpeg_hwaccel=ffmpeg_hwaccel,
            video_encoder=video_encoder,
            audio_encoder='aac',
            thread_count=thread_count,
            memory_optimization=memory_optimization,
            ui_scaling=ui_scaling,
            native_features=native_features
        )
    
    def _is_apple_silicon(self) -> bool:
        """Detecta se está rodando em Apple Silicon (M1/M2/M3/M4)"""
        if platform.system() != 'Darwin':
            return False
        
        try:
            # Verificar através do sysctl
            result = subprocess.run(
                ['sysctl', '-n', 'machdep.cpu.brand_string'],
                capture_output=True,
                text=True,
                check=True
            )
            cpu_brand = result.stdout.strip().lower()
            
            # Verificar se é Apple Silicon
            apple_silicon_indicators = ['apple m1', 'apple m2', 'apple m3', 'apple m4']
            return any(indicator in cpu_brand for indicator in apple_silicon_indicators)
        
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: verificar arquitetura
            machine = platform.machine().lower()
            return machine in ['arm64', 'aarch64']
    
    def _get_hardware_acceleration(self) -> tuple[str, str]:
        """Retorna a configuração de aceleração de hardware apropriada"""
        if self._config and self._config.is_apple_silicon:
            # Apple Silicon: usar VideoToolbox
            return 'videotoolbox', 'h264_videotoolbox'
        elif self._config and self._config.is_macos:
            # macOS Intel: usar VideoToolbox quando disponível
            if self._check_videotoolbox_support():
                return 'videotoolbox', 'h264_videotoolbox'
            else:
                return 'auto', 'libx264'
        elif platform.system().lower() == 'windows':
            # Windows: tentar NVENC, depois DXVA2, fallback para software
            if self._check_nvenc_support():
                return 'cuda', 'h264_nvenc'
            elif self._check_dxva2_support():
                return 'dxva2', 'h264_qsv'
            else:
                return 'auto', 'libx264'
        else:
            # Linux e outros: tentar VAAPI, depois software
            if self._check_vaapi_support():
                return 'vaapi', 'h264_vaapi'
            else:
                return 'auto', 'libx264'
    
    def _check_videotoolbox_support(self) -> bool:
        """Verifica se VideoToolbox está disponível"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-hide_banner', '-encoders'],
                capture_output=True,
                text=True,
                check=True
            )
            return 'h264_videotoolbox' in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_nvenc_support(self) -> bool:
        """Verifica se NVENC está disponível"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-hide_banner', '-encoders'],
                capture_output=True,
                text=True,
                check=True
            )
            return 'h264_nvenc' in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_dxva2_support(self) -> bool:
        """Verifica se DXVA2/QSV está disponível"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-hide_banner', '-encoders'],
                capture_output=True,
                text=True,
                check=True
            )
            return 'h264_qsv' in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_vaapi_support(self) -> bool:
        """Verifica se VAAPI está disponível"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-hide_banner', '-encoders'],
                capture_output=True,
                text=True,
                check=True
            )
            return 'h264_vaapi' in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_optimal_thread_count(self) -> int:
        """Retorna o número otimizado de threads para a plataforma"""
        cpu_count = os.cpu_count() or 4
        
        if self._config and self._config.is_apple_silicon:
            # Apple Silicon: usar todos os cores de performance + metade dos efficiency
            # Aproximação: usar 75% dos cores disponíveis
            return max(4, int(cpu_count * 0.75))
        elif platform.system().lower() == 'darwin':
            # macOS Intel: usar 80% dos cores
            return max(2, int(cpu_count * 0.8))
        else:
            # Windows/Linux: usar 90% dos cores
            return max(2, int(cpu_count * 0.9))
    
    def _get_memory_optimization(self) -> Dict[str, Any]:
        """Retorna configurações de otimização de memória"""
        if self._config and self._config.is_apple_silicon:
            return {
                'buffer_size': '64M',
                'max_muxing_queue_size': 1024,
                'thread_queue_size': 512,
                'use_unified_memory': True
            }
        elif platform.system().lower() == 'darwin':
            return {
                'buffer_size': '32M',
                'max_muxing_queue_size': 512,
                'thread_queue_size': 256,
                'use_unified_memory': False
            }
        else:
            return {
                'buffer_size': '16M',
                'max_muxing_queue_size': 256,
                'thread_queue_size': 128,
                'use_unified_memory': False
            }
    
    def _get_ui_scaling(self) -> float:
        """Retorna o fator de escala da UI apropriado"""
        if platform.system().lower() == 'darwin':
            try:
                # Detectar densidade de pixels no macOS
                result = subprocess.run(
                    ['system_profiler', 'SPDisplaysDataType'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if 'Retina' in result.stdout or '5K' in result.stdout or '6K' in result.stdout:
                    return 2.0
                elif '4K' in result.stdout:
                    return 1.5
                else:
                    return 1.0
            except (subprocess.CalledProcessError, FileNotFoundError):
                return 1.0
        else:
            return 1.0
    
    def _get_native_features(self) -> Dict[str, bool]:
        """Retorna recursos nativos disponíveis por plataforma"""
        if platform.system().lower() == 'darwin':
            return {
                'menu_bar_integration': True,
                'notification_center': True,
                'drag_and_drop': True,
                'dark_mode_detection': True,
                'window_transparency': True,
                'metal_rendering': self._config.is_apple_silicon if self._config else False,
                'spotlight_integration': True,
                'quick_look': True
            }
        elif platform.system().lower() == 'windows':
            return {
                'menu_bar_integration': False,
                'notification_center': True,
                'drag_and_drop': True,
                'dark_mode_detection': True,
                'window_transparency': True,
                'metal_rendering': False,
                'spotlight_integration': False,
                'quick_look': False
            }
        else:
            return {
                'menu_bar_integration': False,
                'notification_center': False,
                'drag_and_drop': True,
                'dark_mode_detection': False,
                'window_transparency': False,
                'metal_rendering': False,
                'spotlight_integration': False,
                'quick_look': False
            }
    
    @property
    def config(self) -> PlatformConfig:
        """Retorna a configuração da plataforma"""
        if self._config is None:
            self._detect_platform()
        return self._config
    
    def get_ffmpeg_base_args(self) -> list[str]:
        """Retorna argumentos base do FFmpeg otimizados para a plataforma"""
        config = self.config
        args = ['ffmpeg']
        
        # Adicionar aceleração de hardware
        if config.ffmpeg_hwaccel != 'auto':
            args.extend(['-hwaccel', config.ffmpeg_hwaccel])
        
        # Configurações específicas do Apple Silicon
        if config.is_apple_silicon:
            args.extend([
                '-hwaccel_output_format', 'videotoolbox_vld',
                '-threads', str(config.thread_count)
            ])
        
        return args
    
    def get_encoding_args(self, vertical: bool = False) -> list[str]:
        """Retorna argumentos de codificação otimizados"""
        config = self.config
        args = []
        
        # Configurar encoder de vídeo
        args.extend(['-c:v', config.video_encoder])
        
        # Configurações específicas por encoder
        if config.video_encoder == 'h264_videotoolbox':
            args.extend([
                '-b:v', '8M' if not vertical else '6M',
                '-maxrate', '12M' if not vertical else '9M',
                '-bufsize', '16M' if not vertical else '12M',
                '-profile:v', 'high',
                '-level', '4.1',
                '-allow_sw', '1'
            ])
        elif config.video_encoder == 'h264_nvenc':
            args.extend([
                '-preset', 'p7',
                '-cq', '20',
                '-profile:v', 'high',
                '-rc', 'vbr_hq',
                '-bf', '4'
            ])
        else:
            # Software encoding
            args.extend([
                '-preset', 'medium',
                '-crf', '20',
                '-profile:v', 'high',
                '-level', '4.1'
            ])
        
        # Configurar filtros de vídeo
        if vertical:
            if config.is_apple_silicon:
                # Usar Metal para processamento no Apple Silicon
                args.extend(['-vf', "crop=ih*(9/16):ih:(iw-ih*(9/16))/2:0,scale=1080:1920:flags=lanczos"])
            else:
                args.extend(['-vf', "crop=ih*(9/16):ih:(iw-ih*(9/16))/2:0,scale=1080:1920"])
        
        # Configurar áudio
        args.extend(['-c:a', config.audio_encoder, '-b:a', '256k'])
        
        # Otimizações de streaming
        args.extend(['-movflags', '+faststart'])
        
        return args

# Instância global do detector
platform_detector = PlatformDetector()

def get_platform_config() -> PlatformConfig:
    """Função de conveniência para obter a configuração da plataforma"""
    return platform_detector.config

def is_apple_silicon() -> bool:
    """Função de conveniência para verificar se está rodando em Apple Silicon"""
    return platform_detector.config.is_apple_silicon

def is_macos() -> bool:
    """Função de conveniência para verificar se está rodando em macOS"""
    return platform_detector.config.is_macos

def is_windows() -> bool:
    """Função de conveniência para verificar se está rodando em Windows"""
    return platform_detector.config.is_windows