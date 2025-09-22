#!/usr/bin/env python3
"""
Script para otimizar imagens do projeto
Converte imagens para formatos modernos (WebP, AVIF) e redimensiona conforme necessário
"""

import os
import sys
from pathlib import Path
from PIL import Image
import argparse

def optimize_image(input_path, output_path, max_width=None, max_height=None, quality=85):
    """
    Otimiza uma imagem redimensionando e convertendo para WebP
    """
    try:
        with Image.open(input_path) as img:
            # Converter para RGB se necessário
            if img.mode in ('RGBA', 'LA', 'P'):
                # Criar fundo branco para imagens com transparência
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionar se necessário
            if max_width or max_height:
                img.thumbnail((max_width or img.width, max_height or img.height), Image.Resampling.LANCZOS)
            
            # Salvar como WebP
            img.save(output_path, 'WEBP', quality=quality, optimize=True)
            
            # Calcular economia de espaço
            original_size = os.path.getsize(input_path)
            optimized_size = os.path.getsize(output_path)
            savings = ((original_size - optimized_size) / original_size) * 100
            
            print(f"✓ {input_path.name} -> {output_path.name} ({savings:.1f}% menor)")
            
    except Exception as e:
        print(f"✗ Erro ao processar {input_path}: {e}")

def create_webp_versions(image_dir, max_width=1200, max_height=800, quality=85):
    """
    Cria versões WebP de todas as imagens em um diretório
    """
    image_dir = Path(image_dir)
    webp_dir = image_dir / 'webp'
    webp_dir.mkdir(exist_ok=True)
    
    # Extensões de imagem suportadas
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    processed = 0
    for image_file in image_dir.glob('*'):
        if image_file.suffix.lower() in image_extensions:
            webp_path = webp_dir / f"{image_file.stem}.webp"
            
            # Só processar se o WebP não existir ou for mais antigo
            if not webp_path.exists() or image_file.stat().st_mtime > webp_path.stat().st_mtime:
                optimize_image(image_file, webp_path, max_width, max_height, quality)
                processed += 1
            else:
                print(f"⏭ {image_file.name} já tem versão WebP atualizada")
    
    print(f"\nProcessadas {processed} imagens")

def generate_srcset(image_path, sizes=[400, 800, 1200]):
    """
    Gera atributo srcset para uma imagem
    """
    image_path = Path(image_path)
    webp_dir = image_path.parent / 'webp'
    
    srcset_parts = []
    for size in sizes:
        webp_file = webp_dir / f"{image_path.stem}_{size}w.webp"
        if webp_file.exists():
            srcset_parts.append(f"{webp_file} {size}w")
    
    return ", ".join(srcset_parts)

def main():
    parser = argparse.ArgumentParser(description='Otimizar imagens do projeto')
    parser.add_argument('--dir', default='static/core/images', help='Diretório com imagens')
    parser.add_argument('--max-width', type=int, default=1200, help='Largura máxima')
    parser.add_argument('--max-height', type=int, default=800, help='Altura máxima')
    parser.add_argument('--quality', type=int, default=85, help='Qualidade WebP (1-100)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dir):
        print(f"Diretório {args.dir} não encontrado!")
        sys.exit(1)
    
    print(f"Otimizando imagens em {args.dir}...")
    create_webp_versions(args.dir, args.max_width, args.max_height, args.quality)
    print("Otimização concluída!")

if __name__ == '__main__':
    main() 