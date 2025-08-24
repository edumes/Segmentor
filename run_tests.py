#!/usr/bin/env python3
"""
Script para executar testes automatizados de compatibilidade multiplataforma
Gera relatórios específicos para cada plataforma
"""

import sys
import os
import subprocess
import platform
import json
import time
from pathlib import Path
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.python_executable = sys.executable
        self.project_root = Path.cwd()
        self.test_results_dir = self.project_root / "test_results"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup_test_environment(self):
        """Configura o ambiente de teste"""
        print("🔧 Configurando ambiente de teste...")
        
        # Criar diretório de resultados
        self.test_results_dir.mkdir(exist_ok=True)
        
        # Verificar se pytest está instalado
        try:
            subprocess.run(
                [self.python_executable, '-m', 'pytest', '--version'],
                check=True,
                capture_output=True
            )
            print("✅ pytest encontrado")
        except subprocess.CalledProcessError:
            print("❌ pytest não encontrado. Instalando...")
            subprocess.run(
                [self.python_executable, '-m', 'pip', 'install', 'pytest', 'pytest-cov', 'pytest-html'],
                check=True
            )
            print("✅ pytest instalado")
        
        # Verificar dependências do projeto
        self.check_project_dependencies()
        
    def check_project_dependencies(self):
        """Verifica se as dependências do projeto estão instaladas"""
        print("🔍 Verificando dependências do projeto...")
        
        required_modules = ['PyQt6', 'cv2', 'numpy', 'PIL']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module} disponível")
            except ImportError:
                missing_modules.append(module)
                print(f"❌ {module} não encontrado")
        
        if missing_modules:
            print(f"⚠️  Módulos faltando: {', '.join(missing_modules)}")
            print("   Execute 'python install.py' primeiro")
            return False
        
        return True
    
    def run_platform_detection_tests(self):
        """Executa testes de detecção de plataforma"""
        print("\n🧪 Executando testes de detecção de plataforma...")
        
        cmd = [
            self.python_executable, '-m', 'pytest',
            'test_platform_compatibility.py::TestPlatformDetection',
            '-v',
            '--tb=short',
            f'--html={self.test_results_dir}/platform_detection_{self.timestamp}.html',
            '--self-contained-html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return self.process_test_result("Platform Detection", result)
    
    def run_video_processing_tests(self):
        """Executa testes de processamento de vídeo"""
        print("\n🎥 Executando testes de processamento de vídeo...")
        
        cmd = [
            self.python_executable, '-m', 'pytest',
            'test_platform_compatibility.py::TestVideoProcessing',
            '-v',
            '--tb=short',
            f'--html={self.test_results_dir}/video_processing_{self.timestamp}.html',
            '--self-contained-html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return self.process_test_result("Video Processing", result)
    
    def run_ui_compatibility_tests(self):
        """Executa testes de compatibilidade da UI"""
        print("\n🖥️  Executando testes de compatibilidade da UI...")
        
        # Configurar variáveis de ambiente para testes de UI
        env = os.environ.copy()
        env['QT_QPA_PLATFORM'] = 'offscreen'
        env['DISPLAY'] = ':99' if self.system == 'linux' else env.get('DISPLAY', '')
        
        cmd = [
            self.python_executable, '-m', 'pytest',
            'test_platform_compatibility.py::TestUICompatibility',
            '-v',
            '--tb=short',
            f'--html={self.test_results_dir}/ui_compatibility_{self.timestamp}.html',
            '--self-contained-html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        return self.process_test_result("UI Compatibility", result)
    
    def run_ffmpeg_tests(self):
        """Executa testes de compatibilidade do FFmpeg"""
        print("\n🎬 Executando testes de compatibilidade do FFmpeg...")
        
        cmd = [
            self.python_executable, '-m', 'pytest',
            'test_platform_compatibility.py::TestFFmpegCompatibility',
            '-v',
            '--tb=short',
            f'--html={self.test_results_dir}/ffmpeg_compatibility_{self.timestamp}.html',
            '--self-contained-html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return self.process_test_result("FFmpeg Compatibility", result)
    
    def run_performance_tests(self):
        """Executa testes de performance"""
        print("\n⚡ Executando testes de performance...")
        
        cmd = [
            self.python_executable, '-m', 'pytest',
            'test_platform_compatibility.py::TestPerformanceOptimizations',
            '-v',
            '--tb=short',
            f'--html={self.test_results_dir}/performance_{self.timestamp}.html',
            '--self-contained-html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return self.process_test_result("Performance Optimizations", result)
    
    def run_platform_specific_tests(self):
        """Executa testes específicos da plataforma atual"""
        print(f"\n🔧 Executando testes específicos para {self.system.title()}...")
        
        if self.system == 'darwin':
            marker = 'macos'
        elif self.system == 'windows':
            marker = 'windows'
        else:
            marker = 'linux'
        
        cmd = [
            self.python_executable, '-m', 'pytest',
            'test_platform_compatibility.py',
            '-v',
            '--tb=short',
            '-m', marker,
            f'--html={self.test_results_dir}/platform_specific_{self.timestamp}.html',
            '--self-contained-html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return self.process_test_result(f"Platform Specific ({self.system.title()})", result)
    
    def run_all_tests(self):
        """Executa todos os testes com cobertura"""
        print("\n🧪 Executando todos os testes com cobertura...")
        
        cmd = [
            self.python_executable, '-m', 'pytest',
            'test_platform_compatibility.py',
            '-v',
            '--tb=short',
            '--cov=.',
            '--cov-report=term-missing',
            f'--cov-report=html:{self.test_results_dir}/coverage_{self.timestamp}',
            f'--html={self.test_results_dir}/all_tests_{self.timestamp}.html',
            '--self-contained-html'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return self.process_test_result("All Tests", result)
    
    def process_test_result(self, test_name, result):
        """Processa resultado de teste e retorna informações"""
        success = result.returncode == 0
        
        # Extrair estatísticas do output
        output_lines = result.stdout.split('\n')
        stats = self.extract_test_stats(output_lines)
        
        test_result = {
            'name': test_name,
            'success': success,
            'returncode': result.returncode,
            'stats': stats,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'timestamp': datetime.now().isoformat()
        }
        
        # Salvar resultado individual
        result_file = self.test_results_dir / f"{test_name.lower().replace(' ', '_')}_{self.timestamp}.json"
        with open(result_file, 'w') as f:
            json.dump(test_result, f, indent=2)
        
        # Exibir resultado
        if success:
            print(f"✅ {test_name}: {stats.get('passed', 0)} passou, {stats.get('failed', 0)} falhou")
        else:
            print(f"❌ {test_name}: {stats.get('passed', 0)} passou, {stats.get('failed', 0)} falhou")
            if result.stderr:
                print(f"   Erro: {result.stderr[:200]}...")
        
        return test_result
    
    def extract_test_stats(self, output_lines):
        """Extrai estatísticas dos testes do output do pytest"""
        stats = {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 0}
        
        for line in output_lines:
            if 'passed' in line and 'failed' in line:
                # Linha de resumo do pytest
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed':
                        try:
                            stats['passed'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'failed':
                        try:
                            stats['failed'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'skipped':
                        try:
                            stats['skipped'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'error' or part == 'errors':
                        try:
                            stats['errors'] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
        
        return stats
    
    def generate_summary_report(self, all_results):
        """Gera relatório resumo de todos os testes"""
        print("\n📊 Gerando relatório resumo...")
        
        summary = {
            'platform': {
                'system': platform.system(),
                'machine': platform.machine(),
                'python_version': sys.version,
                'timestamp': datetime.now().isoformat()
            },
            'results': all_results,
            'overall_success': all(r['success'] for r in all_results),
            'total_stats': {
                'passed': sum(r['stats'].get('passed', 0) for r in all_results),
                'failed': sum(r['stats'].get('failed', 0) for r in all_results),
                'skipped': sum(r['stats'].get('skipped', 0) for r in all_results),
                'errors': sum(r['stats'].get('errors', 0) for r in all_results)
            }
        }
        
        # Salvar relatório resumo
        summary_file = self.test_results_dir / f"test_summary_{self.timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Gerar relatório em texto
        self.generate_text_report(summary)
        
        return summary
    
    def generate_text_report(self, summary):
        """Gera relatório em texto legível"""
        report_file = self.test_results_dir / f"test_report_{self.timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE TESTES DE COMPATIBILIDADE MULTIPLATAFORMA\n")
            f.write("=" * 80 + "\n\n")
            
            # Informações da plataforma
            f.write("INFORMAÇÕES DA PLATAFORMA:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Sistema: {summary['platform']['system']}\n")
            f.write(f"Arquitetura: {summary['platform']['machine']}\n")
            f.write(f"Python: {summary['platform']['python_version'].split()[0]}\n")
            f.write(f"Data/Hora: {summary['platform']['timestamp']}\n\n")
            
            # Resumo geral
            f.write("RESUMO GERAL:\n")
            f.write("-" * 40 + "\n")
            stats = summary['total_stats']
            f.write(f"Testes Passou: {stats['passed']}\n")
            f.write(f"Testes Falhou: {stats['failed']}\n")
            f.write(f"Testes Pulados: {stats['skipped']}\n")
            f.write(f"Erros: {stats['errors']}\n")
            f.write(f"Status Geral: {'✅ SUCESSO' if summary['overall_success'] else '❌ FALHA'}\n\n")
            
            # Detalhes por categoria
            f.write("DETALHES POR CATEGORIA:\n")
            f.write("-" * 40 + "\n")
            
            for result in summary['results']:
                f.write(f"\n{result['name']}:\n")
                f.write(f"  Status: {'✅ PASSOU' if result['success'] else '❌ FALHOU'}\n")
                f.write(f"  Passou: {result['stats'].get('passed', 0)}\n")
                f.write(f"  Falhou: {result['stats'].get('failed', 0)}\n")
                f.write(f"  Pulados: {result['stats'].get('skipped', 0)}\n")
                
                if not result['success'] and result['stderr']:
                    f.write(f"  Erro: {result['stderr'][:200]}...\n")
        
        print(f"📄 Relatório salvo em: {report_file}")
    
    def print_final_summary(self, summary):
        """Exibe resumo final no console"""
        print("\n" + "=" * 80)
        print("    🎯 RESUMO FINAL DOS TESTES")
        print("=" * 80)
        
        stats = summary['total_stats']
        print(f"\n📊 Estatísticas Gerais:")
        print(f"   ✅ Passou: {stats['passed']}")
        print(f"   ❌ Falhou: {stats['failed']}")
        print(f"   ⏭️  Pulados: {stats['skipped']}")
        print(f"   🚨 Erros: {stats['errors']}")
        
        print(f"\n🎯 Status Geral: {'✅ TODOS OS TESTES PASSARAM' if summary['overall_success'] else '❌ ALGUNS TESTES FALHARAM'}")
        
        print(f"\n📁 Resultados salvos em: {self.test_results_dir}")
        print(f"📄 Relatório principal: test_report_{self.timestamp}.txt")
        
        if not summary['overall_success']:
            print("\n⚠️  ATENÇÃO: Alguns testes falharam. Verifique os relatórios detalhados.")
        
        print("=" * 80)
    
    def run(self, test_type='all'):
        """Executa os testes baseado no tipo especificado"""
        print(f"🚀 Iniciando testes de compatibilidade para {platform.system()}...")
        
        self.setup_test_environment()
        
        all_results = []
        
        if test_type in ['all', 'platform']:
            all_results.append(self.run_platform_detection_tests())
        
        if test_type in ['all', 'video']:
            all_results.append(self.run_video_processing_tests())
        
        if test_type in ['all', 'ui']:
            all_results.append(self.run_ui_compatibility_tests())
        
        if test_type in ['all', 'ffmpeg']:
            all_results.append(self.run_ffmpeg_tests())
        
        if test_type in ['all', 'performance']:
            all_results.append(self.run_performance_tests())
        
        if test_type in ['all', 'specific']:
            all_results.append(self.run_platform_specific_tests())
        
        if test_type == 'all':
            all_results.append(self.run_all_tests())
        
        # Gerar relatório resumo
        summary = self.generate_summary_report(all_results)
        self.print_final_summary(summary)
        
        return summary['overall_success']

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Executar testes de compatibilidade multiplataforma')
    parser.add_argument(
        '--type', 
        choices=['all', 'platform', 'video', 'ui', 'ffmpeg', 'performance', 'specific'],
        default='all',
        help='Tipo de teste a executar (padrão: all)'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        success = runner.run(args.type)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Testes cancelados pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado durante os testes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()