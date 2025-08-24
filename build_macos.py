#!/usr/bin/env python3
"""
Script de build para criar executável .app do Segmentor para macOS

Este script automatiza o processo de:
1. Verificar dependências
2. Converter ícone SVG para .icns
3. Criar executável com PyInstaller
4. Configurar permissões
5. Validar o bundle .app
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class SegmentorBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.assets_dir = self.project_root / "assets"
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
    def check_dependencies(self):
        """Verifica se todas as dependências estão instaladas"""
        print("🔍 Verificando dependências...")
        
        required_packages = [
            ('PyInstaller', 'PyInstaller'),
            ('PyQt6', 'PyQt6'),
            ('opencv-python', 'cv2'),
            ('numpy', 'numpy'),
            ('Pillow', 'PIL')
        ]
        
        missing_packages = []
        for package_name, import_name in required_packages:
            try:
                __import__(import_name)
                print(f"✅ {package_name} - OK")
            except ImportError:
                missing_packages.append(package_name)
                print(f"❌ {package_name} - FALTANDO")
        
        if missing_packages:
            print(f"\n⚠️  Instale as dependências faltantes:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        return True
    
    def convert_icon(self):
        """Converte ícone SVG para .icns usando sips (nativo do macOS)"""
        print("🎨 Convertendo ícone...")
        
        svg_path = self.assets_dir / "icon.svg"
        png_path = self.assets_dir / "icon.png"
        icns_path = self.assets_dir / "icon.icns"
        
        if not svg_path.exists():
            print(f"❌ Arquivo SVG não encontrado: {svg_path}")
            return False
        
        try:
            # Converter SVG para PNG de alta resolução
            subprocess.run([
                'qlmanage', '-t', '-s', '1024', '-o', str(self.assets_dir), str(svg_path)
            ], check=True, capture_output=True)
            
            # Renomear arquivo gerado pelo qlmanage
            generated_png = self.assets_dir / "icon.svg.png"
            if generated_png.exists():
                generated_png.rename(png_path)
            
            # Converter PNG para ICNS
            subprocess.run([
                'sips', '-s', 'format', 'icns', str(png_path), '--out', str(icns_path)
            ], check=True, capture_output=True)
            
            # Limpar arquivo PNG temporário
            if png_path.exists():
                png_path.unlink()
            
            print(f"✅ Ícone convertido: {icns_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao converter ícone: {e}")
            # Fallback: criar um ícone básico
            return self.create_fallback_icon()
    
    def create_fallback_icon(self):
        """Cria um ícone básico caso a conversão falhe"""
        print("🔄 Criando ícone alternativo...")
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Criar imagem 512x512
            img = Image.new('RGBA', (512, 512), (74, 144, 226, 255))
            draw = ImageDraw.Draw(img)
            
            # Desenhar círculo
            draw.ellipse([50, 50, 462, 462], fill=(255, 255, 255, 200))
            
            # Adicionar texto
            try:
                font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 60)
            except:
                font = ImageFont.load_default()
            
            text = "SEG"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (512 - text_width) // 2
            y = (512 - text_height) // 2
            
            draw.text((x, y), text, fill=(74, 144, 226, 255), font=font)
            
            # Salvar como PNG e converter para ICNS
            png_path = self.assets_dir / "icon.png"
            img.save(png_path, 'PNG')
            
            icns_path = self.assets_dir / "icon.icns"
            subprocess.run([
                'sips', '-s', 'format', 'icns', str(png_path), '--out', str(icns_path)
            ], check=True, capture_output=True)
            
            png_path.unlink()
            print("✅ Ícone alternativo criado")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar ícone alternativo: {e}")
            return False
    
    def clean_build_dirs(self):
        """Limpa diretórios de build anteriores"""
        print("🧹 Limpando builds anteriores...")
        
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    print(f"✅ Removido: {dir_path}")
                except Exception as e:
                    print(f"⚠️  Aviso ao remover {dir_path}: {e}")
        
        return True
    
    def build_app(self):
        """Executa PyInstaller para criar o .app"""
        print("🔨 Construindo aplicativo...")
        
        spec_file = self.project_root / "segmentor.spec"
        
        if not spec_file.exists():
            print(f"❌ Arquivo spec não encontrado: {spec_file}")
            return False
        
        try:
            cmd = [sys.executable, '-m', 'PyInstaller', '--clean', str(spec_file)]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Erro no PyInstaller:")
                print(result.stderr)
                return False
            
            print("✅ Build concluído com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro durante build: {e}")
            return False
    
    def set_permissions(self):
        """Configura permissões corretas para o .app"""
        print("🔐 Configurando permissões...")
        
        app_path = self.dist_dir / "Segmentor.app"
        
        if not app_path.exists():
            print(f"❌ Aplicativo não encontrado: {app_path}")
            return False
        
        try:
            # Tornar executável
            subprocess.run(['chmod', '+x', str(app_path / "Contents" / "MacOS" / "Segmentor")], check=True)
            
            # Configurar permissões do bundle
            subprocess.run(['chmod', '-R', '755', str(app_path)], check=True)
            
            print("✅ Permissões configuradas")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao configurar permissões: {e}")
            return False
    
    def validate_app(self):
        """Valida o bundle .app criado"""
        print("✅ Validando aplicativo...")
        
        app_path = self.dist_dir / "Segmentor.app"
        
        # Verificar estrutura básica
        required_paths = [
            app_path / "Contents",
            app_path / "Contents" / "MacOS" / "Segmentor",
            app_path / "Contents" / "Info.plist",
            app_path / "Contents" / "Resources"
        ]
        
        for path in required_paths:
            if not path.exists():
                print(f"❌ Arquivo/diretório faltando: {path}")
                return False
        
        # Verificar se é executável
        executable = app_path / "Contents" / "MacOS" / "Segmentor"
        if not os.access(executable, os.X_OK):
            print(f"❌ Executável sem permissão: {executable}")
            return False
        
        print("✅ Aplicativo validado com sucesso")
        print(f"📦 Aplicativo criado em: {app_path}")
        return True
    
    def build(self):
        """Executa todo o processo de build"""
        print("🚀 Iniciando build do Segmentor para macOS...\n")
        
        steps = [
            ("Verificar dependências", self.check_dependencies),
            ("Converter ícone", self.convert_icon),
            ("Limpar builds anteriores", self.clean_build_dirs),
            ("Construir aplicativo", self.build_app),
            ("Configurar permissões", self.set_permissions),
            ("Validar aplicativo", self.validate_app)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"\n❌ Build falhou na etapa: {step_name}")
                return False
        
        print("\n🎉 Build concluído com sucesso!")
        print(f"\n📱 Seu aplicativo está pronto em: {self.dist_dir / 'Segmentor.app'}")
        print("\n💡 Para testar, execute: open dist/Segmentor.app")
        return True

def main():
    if sys.platform != 'darwin':
        print("❌ Este script deve ser executado no macOS")
        sys.exit(1)
    
    builder = SegmentorBuilder()
    success = builder.build()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()