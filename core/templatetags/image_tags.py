from django import template
from django.conf import settings
from django.templatetags.static import static
from pathlib import Path
import os

register = template.Library()

@register.simple_tag
def responsive_image(image_path, alt_text="", class_name="", sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"):
    """
    Template tag para gerar imagens responsivas com WebP e fallback
    """
    if not image_path:
        return ""
    
    # Verificar se existe versão WebP
    static_root = Path(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') else Path(settings.STATICFILES_DIRS[0])
    image_path_obj = Path(image_path)
    
    # Caminho para versão WebP
    webp_path = image_path_obj.parent / 'webp' / f"{image_path_obj.stem}.webp"
    webp_static_path = static_root / webp_path
    
    # Verificar se WebP existe
    has_webp = webp_static_path.exists()
    
    # Gerar HTML da imagem
    html = '<picture>'
    
    # WebP se disponível
    if has_webp:
        html += f'<source srcset="{static(str(webp_path))}" type="image/webp">'
    
    # Fallback original
    html += f'<img src="{static(image_path)}" alt="{alt_text}" class="{class_name}" loading="lazy" decoding="async">'
    html += '</picture>'
    
    return html

@register.simple_tag
def optimized_image(image_path, alt_text="", class_name="", width=None, height=None):
    """
    Template tag para imagens otimizadas com dimensões específicas
    """
    if not image_path:
        return ""
    
    # Verificar se existe versão WebP
    static_root = Path(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') else Path(settings.STATICFILES_DIRS[0])
    image_path_obj = Path(image_path)
    
    # Caminho para versão WebP
    webp_path = image_path_obj.parent / 'webp' / f"{image_path_obj.stem}.webp"
    webp_static_path = static_root / webp_path
    
    # Verificar se WebP existe
    has_webp = webp_static_path.exists()
    
    # Atributos da imagem
    img_attrs = f'src="{static(image_path)}" alt="{alt_text}" class="{class_name}" loading="lazy" decoding="async"'
    if width:
        img_attrs += f' width="{width}"'
    if height:
        img_attrs += f' height="{height}"'
    
    # Gerar HTML da imagem
    html = '<picture>'
    
    # WebP se disponível
    if has_webp:
        html += f'<source srcset="{static(str(webp_path))}" type="image/webp">'
    
    # Fallback original
    html += f'<img {img_attrs}>'
    html += '</picture>'
    
    return html

@register.simple_tag
def preload_image(image_path):
    """
    Template tag para preload de imagens críticas
    """
    if not image_path:
        return ""
    
    # Verificar se existe versão WebP
    static_root = Path(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') else Path(settings.STATICFILES_DIRS[0])
    image_path_obj = Path(image_path)
    
    # Caminho para versão WebP
    webp_path = image_path_obj.parent / 'webp' / f"{image_path_obj.stem}.webp"
    webp_static_path = static_root / webp_path
    
    # Verificar se WebP existe
    has_webp = webp_static_path.exists()
    
    html = f'<link rel="preload" as="image" href="{static(image_path)}">'
    if has_webp:
        html += f'<link rel="preload" as="image" href="{static(str(webp_path))}">'
    
    return html 