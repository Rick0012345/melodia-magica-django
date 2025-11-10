// Variáveis globais
let sessionId = null;
let isTyping = false;

// Inicialização do chatbot
document.addEventListener('DOMContentLoaded', function() {
    // Definir horário da mensagem de boas-vindas
    const welcomeTime = document.getElementById('welcome-time');
    if (welcomeTime) {
        welcomeTime.textContent = getCurrentTime();
    }
    
    // Adicionar event listeners
    const input = document.getElementById('chatbot-input');
    const sendButton = document.getElementById('chatbot-send');
    
    if (input) {
        // Usar 'keydown' pois 'keypress' é deprecado e pode não disparar para Enter
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        input.addEventListener('input', function() {
            // Habilitar/desabilitar botão de envio baseado no conteúdo
            if (sendButton) {
                if (this.value.trim()) {
                    sendButton.style.opacity = '1';
                    sendButton.style.cursor = 'pointer';
                } else {
                    sendButton.style.opacity = '0.6';
                    sendButton.style.cursor = 'not-allowed';
                }
            }
        });
    }
    
    // Carregar histórico se usuário estiver logado
    loadChatHistory();
});

// Função para abrir/fechar o chatbot
function toggleChatbot() {
    const modal = document.getElementById('chatbot-modal');
    if (modal.style.display === 'block') {
        closeChatbot();
    } else {
        openChatbot();
    }
}

// Função para abrir o chatbot
function openChatbot() {
    const modal = document.getElementById('chatbot-modal');
    modal.style.display = 'block';
    
    // Focar no input
    setTimeout(() => {
        const input = document.getElementById('chatbot-input');
        if (input) {
            input.focus();
        }
    }, 300);
    
    // Scroll para o final das mensagens
    scrollToBottom();
}

// Função para fechar o chatbot
function closeChatbot() {
    const modal = document.getElementById('chatbot-modal');
    modal.style.display = 'none';
}

// Função para enviar mensagem
function sendMessage() {
    if (isTyping) return;
    
    const input = document.getElementById('chatbot-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Adicionar mensagem do usuário
    addMessage(message, 'user');
    
    // Limpar input
    input.value = '';
    input.dispatchEvent(new Event('input')); // Trigger input event
    
    // Mostrar indicador de digitação
    showTypingIndicator();
    
    // Enviar para o servidor
    sendToServer(message);
}

// Função para enviar sugestão
function sendSuggestion(text) {
    const input = document.getElementById('chatbot-input');
    input.value = text;
    sendMessage();
}

// Função para adicionar mensagem na interface
function addMessage(text, sender) {
    const messagesContainer = document.getElementById('chatbot-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textP = document.createElement('p');
    textP.textContent = text;
    contentDiv.appendChild(textP);
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = getCurrentTime();
    
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll para o final
    scrollToBottom();
}

// Função para mostrar indicador de digitação
function showTypingIndicator() {
    isTyping = true;
    const messagesContainer = document.getElementById('chatbot-messages');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing-indicator';
    typingDiv.id = 'typing-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<p>🤖 está digitando...</p>';
    
    typingDiv.appendChild(contentDiv);
    messagesContainer.appendChild(typingDiv);
    
    scrollToBottom();
}

// Função para remover indicador de digitação
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    isTyping = false;
}

// Função para enviar mensagem para o servidor
async function sendToServer(message) {
    try {
        const response = await fetch('/chatbot/message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remover indicador de digitação
        removeTypingIndicator();
        
        // Adicionar resposta do bot
        if (data.response) {
            addMessage(data.response, 'bot');
        }
        
        // Salvar session_id se fornecido
        if (data.session_id) {
            sessionId = data.session_id;
        }
        
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        removeTypingIndicator();
        addMessage('Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.', 'bot');
    }
}

// Função para carregar histórico de conversas
async function loadChatHistory() {
    try {
        const response = await fetch('/chatbot/history/');
        if (response.ok) {
            const data = await response.json();
            if (data.history && data.history.length > 0) {
                // Limpar mensagem de boas-vindas
                const messagesContainer = document.getElementById('chatbot-messages');
                messagesContainer.innerHTML = '';
                
                // Adicionar histórico
                data.history.reverse().forEach(item => {
                    addMessage(item.message, 'user');
                    addMessage(item.response, 'bot');
                });
            }
        }
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
    }
}

// Função para obter token CSRF
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

// Função para obter hora atual formatada
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Função para scroll para o final das mensagens
function scrollToBottom() {
    const messagesContainer = document.getElementById('chatbot-messages');
    if (messagesContainer) {
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }
}

// Fechar modal ao clicar fora dele
document.addEventListener('click', function(e) {
    const modal = document.getElementById('chatbot-modal');
    const toggle = document.querySelector('.chatbot-toggle');
    
    if (modal && e.target === modal) {
        closeChatbot();
    }
});

// Prevenir fechamento ao clicar dentro do conteúdo
document.addEventListener('click', function(e) {
    const content = document.querySelector('.chatbot-content');
    if (content && content.contains(e.target)) {
        e.stopPropagation();
    }
});