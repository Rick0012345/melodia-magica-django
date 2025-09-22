# Sistema de Mensagens - Melodia Mágica

## Visão Geral

O sistema de mensagens foi criado para fornecer feedback visual aos usuários de forma consistente e profissional. Ele suporta mensagens globais (que aparecem no canto superior direito) e mensagens locais (que aparecem dentro de páginas específicas).

## Funcionalidades

- ✅ Mensagens com diferentes tipos (success, error, warning, info)
- ✅ Animações suaves de entrada e saída
- ✅ Auto-remoção após 5 segundos
- ✅ Botão de fechar manual
- ✅ Responsivo para dispositivos móveis
- ✅ Criação dinâmica de mensagens via JavaScript
- ✅ Compatibilidade com mensagens do Django

## Como Usar

### 1. Mensagens do Django (Backend)

```python
from django.contrib import messages

# Mensagem de sucesso
messages.success(request, 'Operação realizada com sucesso!')

# Mensagem de erro
messages.error(request, 'Ocorreu um erro. Tente novamente.')

# Mensagem de aviso
messages.warning(request, 'Atenção: Esta ação não pode ser desfeita.')

# Mensagem informativa
messages.info(request, 'Nova funcionalidade disponível!')
```

### 2. Mensagens Dinâmicas (Frontend)

```javascript
// Verificar se o MessageManager está disponível
if (window.messageManager) {
    // Mensagem de sucesso
    window.messageManager.success('Operação realizada com sucesso!');
    
    // Mensagem de erro
    window.messageManager.error('Ocorreu um erro!');
    
    // Mensagem de aviso
    window.messageManager.warning('Atenção!');
    
    // Mensagem informativa
    window.messageManager.info('Informação importante!');
}
```

### 3. Mensagens Locais vs Globais

```javascript
// Mensagem global (canto superior direito)
window.messageManager.success('Mensagem global!', true);

// Mensagem local (dentro da página)
window.messageManager.success('Mensagem local!', false);
```

## Estrutura dos Arquivos

```
core/
├── static/
│   └── core/
│       ├── css/
│       │   └── messages.css          # Estilos das mensagens
│       └── js/
│           └── messages.js           # Lógica JavaScript
└── templates/
    └── core/
        ├── base.html                 # Template base com sistema global
        ├── contato.html              # Exemplo de mensagens locais
        ├── menu.html                 # Mensagens informativas
        └── niveis.html               # Mensagens sobre quizzes
```

## Tipos de Mensagem

| Tipo | Cor | Ícone | Uso |
|------|-----|-------|-----|
| `success` | Verde | ✓ | Operações bem-sucedidas |
| `error` | Vermelho | ✗ | Erros e falhas |
| `warning` | Laranja | ⚠ | Avisos e alertas |
| `info` | Azul | ℹ | Informações gerais |

## Personalização

### Alterar Tempo de Auto-remoção

```javascript
// No arquivo messages.js, altere a linha:
this.autoHideDelay = 5000; // 5 segundos
```

### Alterar Duração da Animação

```javascript
// No arquivo messages.js, altere a linha:
this.animationDuration = 300; // 300ms
```

### Adicionar Novos Tipos de Mensagem

1. Adicione o estilo no `messages.css`:
```css
.message-custom {
    background-color: rgba(128, 0, 128, 0.1);
    border-left-color: #800080;
    color: #800080;
}
```

2. Adicione o método no `messages.js`:
```javascript
custom(text, isGlobal = true) {
    return this.createMessage(text, 'custom', isGlobal);
}
```

## Exemplos de Uso

### Formulário de Contato

```javascript
// Após envio bem-sucedido
window.messageManager.success('Mensagem enviada com sucesso!');

// Após erro de validação
window.messageManager.error('Por favor, preencha todos os campos.');
```

### Quiz

```javascript
// Resposta correta
window.messageManager.success('Parabéns! Resposta correta!');

// Resposta incorreta
window.messageManager.error('Ops! Tente novamente.');

// Quiz finalizado
window.messageManager.info('Quiz finalizado! Veja sua pontuação.');
```

### Login/Logout

```javascript
// Login bem-sucedido
window.messageManager.success('Bem-vindo de volta!');

// Logout
window.messageManager.info('Você foi desconectado.');
```

## Compatibilidade

- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Dispositivos móveis

## Dependências

- Font Awesome (para ícones)
- CSS3 (para animações)
- JavaScript ES6+ (para funcionalidades)

## Troubleshooting

### Mensagens não aparecem

1. Verifique se o arquivo `messages.js` está sendo carregado
2. Verifique se o `MessageManager` está inicializado no console
3. Verifique se não há erros JavaScript no console

### Animações não funcionam

1. Verifique se o CSS está sendo carregado
2. Verifique se o navegador suporta CSS3 animations
3. Verifique se não há conflitos de CSS

### Mensagens não somem automaticamente

1. Verifique se o `autoHideDelay` está configurado corretamente
2. Verifique se não há JavaScript bloqueando o setTimeout
3. Verifique se não há erros no console 