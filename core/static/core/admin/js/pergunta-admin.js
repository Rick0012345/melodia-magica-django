// JavaScript para tornar a interface do admin de perguntas mais dinâmica

document.addEventListener('DOMContentLoaded', function() {
    const tipoSelect = document.getElementById('id_tipo');
    
    if (tipoSelect) {
        // Função para mostrar/ocultar campos baseado no tipo
        function toggleFields() {
            const selectedType = tipoSelect.value;
            
            // Encontrar o fieldset de resposta correta
            const respostaVfFieldset = document.querySelector('.collapse');
            
            if (respostaVfFieldset) {
                if (selectedType === 'verdadeiro_falso') {
                    // Expandir o fieldset
                    respostaVfFieldset.classList.remove('collapsed');
                    respostaVfFieldset.style.display = 'block';
                    
                    // Adicionar classe para destacar
                    respostaVfFieldset.classList.add('expanded-vf');
                } else {
                    // Contrair o fieldset
                    respostaVfFieldset.classList.add('collapsed');
                    
                    // Remover classe de destaque
                    respostaVfFieldset.classList.remove('expanded-vf');
                }
            }
            
            // Adicionar indicador visual do tipo
            updateTipoIndicator(selectedType);
        }
        
        // Função para atualizar indicador visual
        function updateTipoIndicator(tipo) {
            // Remover indicador anterior
            const existingIndicator = document.querySelector('.tipo-indicator');
            if (existingIndicator) {
                existingIndicator.remove();
            }
            
            // Adicionar novo indicador
            if (tipo && tipo !== '') {
                const indicator = document.createElement('span');
                indicator.className = `tipo-indicator tipo-${tipo}`;
                indicator.textContent = tipo.replace('_', ' ');
                
                // Adicionar após o label do campo tipo
                const tipoLabel = document.querySelector('label[for="id_tipo"]');
                if (tipoLabel) {
                    tipoLabel.appendChild(indicator);
                }
            }
        }
        
        // Executar na carga da página
        toggleFields();
        
        // Executar quando o tipo mudar
        tipoSelect.addEventListener('change', toggleFields);
        
        // Adicionar tooltip informativo
        addTooltips();
    }
    
    // Função para adicionar tooltips informativos
    function addTooltips() {
        const tooltips = {
            'multipla_escolha': 'Selecione este tipo para criar questões com múltiplas alternativas. Você poderá adicionar quantas alternativas quiser e marcar uma como correta.',
            'verdadeiro_falso': 'Selecione este tipo para criar questões simples de Verdadeiro ou Falso. Você apenas precisa marcar se a resposta correta é Verdadeiro ou Falso.',
            'texto_livre': 'Selecione este tipo para questões que requerem resposta em texto livre.'
        };
        
        // Adicionar tooltip ao select
        if (tipoSelect) {
            tipoSelect.title = tooltips[tipoSelect.value] || 'Selecione o tipo de questão';
            
            tipoSelect.addEventListener('change', function() {
                this.title = tooltips[this.value] || 'Selecione o tipo de questão';
            });
        }
    }
    
    // Melhorar a experiência do usuário com feedback visual
    function addVisualFeedback() {
        const form = document.querySelector('#pergunta_form');
        if (form) {
            form.addEventListener('submit', function() {
                const submitBtn = form.querySelector('input[type="submit"]');
                if (submitBtn) {
                    submitBtn.value = 'Salvando...';
                    submitBtn.disabled = true;
                }
            });
        }
    }
    
    addVisualFeedback();
});

// Função para validar formulário antes do envio
function validatePerguntaForm() {
    const tipo = document.getElementById('id_tipo').value;
    const pergunta = document.getElementById('id_pergunta').value;
    
    if (!pergunta.trim()) {
        alert('Por favor, preencha o texto da pergunta.');
        return false;
    }
    
    if (tipo === 'verdadeiro_falso') {
        const respostaVf = document.getElementById('id_resposta_verdadeiro_falso');
        if (respostaVf && respostaVf.checked === null) {
            alert('Para questões de Verdadeiro/Falso, você deve definir a resposta correta.');
            return false;
        }
    }
    
    return true;
} 