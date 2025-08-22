// Sistema de gerenciamento de mensagens com jQuery
class MessageManager {
    constructor() {
        this.messages = [];
        this.autoHideDelay = 3000; // 3 segundos
        this.animationDuration = 300; // 300ms
        this.init();
    }

    init() {
        // Inicializar mensagens existentes
        this.initializeExistingMessages();
        
        // Configurar listeners para botões de fechar
        this.setupCloseButtons();
        
        // Auto-remover mensagens após delay
        this.autoHideMessages();
    }

    initializeExistingMessages() {
        const $globalMessages = $('.global-message');
        const $localMessages = $('.message');
        
        $globalMessages.add($localMessages).each((index, message) => {
            const $message = $(message);
            if (!$message.attr('id')) {
                $message.attr('id', `message-${Date.now()}-${index}`);
            }
            this.messages.push($message[0]);
        });
    }

    setupCloseButtons() {
        $(document).on('click', '.global-message-close, .message-close', (e) => {
            const $message = $(e.target).closest('.global-message, .message');
            if ($message.length) {
                this.hideMessage($message[0]);
            }
        });
    }

    autoHideMessages() {
        this.messages.forEach(message => {
            setTimeout(() => {
                this.hideMessage(message);
            }, this.autoHideDelay);
        });
    }

    hideMessage(message) {
        const $message = $(message);
        if (!$message.length || $message.is(':hidden')) {
            return;
        }
        
        // Adicionar classe de fade-out
        $message.addClass('fade-out');
        
        // Remover após animação
        setTimeout(() => {
            if ($message.length) {
                $message.remove();
                // Remover da lista de mensagens
                const index = this.messages.indexOf(message);
                if (index > -1) {
                    this.messages.splice(index, 1);
                }
            }
        }, this.animationDuration);
    }

    // Método para criar nova mensagem dinamicamente
    createMessage(text, type = 'info', isGlobal = true) {
        const messageId = `message-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const messageClass = isGlobal ? 'global-message' : 'message';
        const containerClass = isGlobal ? 'global-messages' : 'messages-container';
        
        // Criar container se não existir usando jQuery
        let $container = $(`.${containerClass}`);
        if (!$container.length) {
            $container = $('<div>').addClass(containerClass);
            if (isGlobal) {
                $container.css({
                    position: 'fixed',
                    top: '20px',
                    right: '20px',
                    zIndex: '9999',
                    maxWidth: '400px'
                });
                $('body').append($container);
            } else {
                // Para mensagens locais, inserir no início do main
                const $main = $('main');
                if ($main.length) {
                    $main.prepend($container);
                }
            }
        }

        // Ícone baseado no tipo
        const iconMap = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        
        const icon = iconMap[type] || iconMap['info'];
        
        // Criar mensagem usando jQuery
        const $message = $(`
            <div id="${messageId}" class="${messageClass} ${messageClass}-${type}">
                <div class="${messageClass}-icon">
                    <i class="${icon}"></i>
                </div>
                <div class="${messageClass}-content">
                    <p>${text}</p>
                </div>
                <button class="${messageClass}-close" onclick="messageManager.hideMessage(this.parentElement)">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `);

        // Adicionar ao container
        $container.append($message);
        this.messages.push($message[0]);

        // Auto-remover após delay
        setTimeout(() => {
            this.hideMessage($message[0]);
        }, this.autoHideDelay);

        return $message[0];
    }

    // Métodos de conveniência para diferentes tipos de mensagem
    success(text, isGlobal = true) {
        return this.createMessage(text, 'success', isGlobal);
    }

    error(text, isGlobal = true) {
        return this.createMessage(text, 'error', isGlobal);
    }

    warning(text, isGlobal = true) {
        return this.createMessage(text, 'warning', isGlobal);
    }

    info(text, isGlobal = true) {
        return this.createMessage(text, 'info', isGlobal);
    }
}

// Função para fechar mensagem (compatibilidade com onclick)
function closeMessage(messageId) {
    const $message = $(`#${messageId}`);
    if ($message.length && window.messageManager) {
        window.messageManager.hideMessage($message[0]);
    }
}

// Inicializar quando o DOM e jQuery estiverem carregados
$(document).ready(function() {
    // Criar instância global do gerenciador de mensagens
    window.messageManager = new MessageManager();
    
    // Expor métodos globalmente para uso em templates
    window.showMessage = function(text, type = 'info', isGlobal = true) {
        return window.messageManager.createMessage(text, type, isGlobal);
    };
    
    window.showSuccess = function(text, isGlobal = true) {
        return window.messageManager.success(text, isGlobal);
    };
    
    window.showError = function(text, isGlobal = true) {
        return window.messageManager.error(text, isGlobal);
    };
    
    window.showWarning = function(text, isGlobal = true) {
        return window.messageManager.warning(text, isGlobal);
    };
    
    window.showInfo = function(text, isGlobal = true) {
        return window.messageManager.info(text, isGlobal);
    };
    
    // Debug
    console.log('MessageManager inicializado com jQuery -', window.messageManager.messages.length, 'mensagens');
    
    // Adicionar animações CSS dinamicamente se não existirem
    if (!document.querySelector('#message-animations')) {
        const style = document.createElement('style');
        style.id = 'message-animations';
        style.textContent = `
            @keyframes slideOut {
                from {
                    opacity: 1;
                    transform: translateY(0);
                }
                to {
                    opacity: 0;
                    transform: translateY(-10px);
                }
            }
            
            @keyframes slideOutRight {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }
        `;
        document.head.appendChild(style);
    }
});

// Exemplo de uso:
// messageManager.success('Operação realizada com sucesso!');
// messageManager.error('Ocorreu um erro!');
// messageManager.warning('Atenção!');
// messageManager.info('Informação importante!');