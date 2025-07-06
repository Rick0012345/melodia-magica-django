// Sistema de gerenciamento de mensagens
class MessageManager {
    constructor() {
        this.messages = [];
        this.autoHideDelay = 5000; // 5 segundos
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
        const globalMessages = document.querySelectorAll('.global-message');
        const localMessages = document.querySelectorAll('.message');
        
        [...globalMessages, ...localMessages].forEach((message, index) => {
            message.id = message.id || `message-${Date.now()}-${index}`;
            this.messages.push(message);
        });
    }

    setupCloseButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.global-message-close') || e.target.closest('.message-close')) {
                const message = e.target.closest('.global-message') || e.target.closest('.message');
                if (message) {
                    this.hideMessage(message);
                }
            }
        });
    }

    autoHideMessages() {
        setTimeout(() => {
            this.messages.forEach(message => {
                this.hideMessage(message);
            });
        }, this.autoHideDelay);
    }

    hideMessage(message) {
        if (!message) return;

        // Determinar tipo de animação baseado na classe
        const isGlobal = message.classList.contains('global-message');
        const animationName = isGlobal ? 'slideOutRight' : 'slideOut';
        
        // Aplicar animação de saída
        message.style.animation = `${animationName} ${this.animationDuration}ms ease-out forwards`;
        
        // Remover elemento após animação
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
            // Remover da lista de mensagens
            this.messages = this.messages.filter(m => m !== message);
        }, this.animationDuration);
    }

    // Método para criar nova mensagem dinamicamente
    createMessage(text, type = 'info', isGlobal = true) {
        const messageId = `message-${Date.now()}`;
        const messageClass = isGlobal ? 'global-message' : 'message';
        const containerClass = isGlobal ? 'global-messages' : 'messages-container';
        
        // Criar container se não existir
        let container = document.querySelector(`.${containerClass}`);
        if (!container) {
            container = document.createElement('div');
            container.className = containerClass;
            if (isGlobal) {
                container.style.position = 'fixed';
                container.style.top = '20px';
                container.style.right = '20px';
                container.style.zIndex = '9999';
                container.style.maxWidth = '400px';
                document.body.appendChild(container);
            } else {
                // Para mensagens locais, inserir no início do main
                const main = document.querySelector('main');
                if (main) {
                    main.insertBefore(container, main.firstChild);
                }
            }
        }

        // Criar mensagem
        const message = document.createElement('div');
        message.id = messageId;
        message.className = `${messageClass} ${messageClass}-${type}`;
        
        // Ícone baseado no tipo
        const iconMap = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        
        const icon = iconMap[type] || iconMap['info'];
        
        message.innerHTML = `
            <div class="${messageClass}-icon">
                <i class="${icon}"></i>
            </div>
            <div class="${messageClass}-content">
                <p>${text}</p>
            </div>
            <button class="${messageClass}-close" onclick="messageManager.hideMessage(this.parentElement)">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Adicionar ao container
        container.appendChild(message);
        this.messages.push(message);

        // Auto-remover após delay
        setTimeout(() => {
            this.hideMessage(message);
        }, this.autoHideDelay);

        return message;
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

// Função global para fechar mensagens (para compatibilidade com onclick)
function closeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message && window.messageManager) {
        window.messageManager.hideMessage(message);
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    window.messageManager = new MessageManager();
    
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