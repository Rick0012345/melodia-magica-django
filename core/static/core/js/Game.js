$(document).ready(function() {
    // Validação do formulário de resposta
    $('#resposta-form').on('submit', function(e) {
        const resposta = $('input[name="resposta"]:checked');
        if (!resposta.length) {
            e.preventDefault();
            alert('Por favor, selecione uma resposta!');
            return;
        }
    });
    
    // Força a atualização da barra de progresso
    const progressBar = $('#progress-bar');
    if (progressBar.length) {
        const progressoValue = progressBar.attr('data-progresso');
        console.log('Valor do progresso:', progressoValue);
        
        // Aplica o valor correto diretamente
        const widthValue = progressoValue ? parseFloat(progressoValue) : 0;
        progressBar.css('width', widthValue + '%');
        
        // Força a reaplicação do estilo com animação
        setTimeout(function() {
            progressBar.css({
                'width': '0%',
                'transition': 'none'
            });
            
            setTimeout(function() {
                progressBar.css({
                    'transition': 'width 0.6s ease',
                    'width': widthValue + '%'
                });
            }, 50);
        }, 100);
        
        // Verifica se a largura foi aplicada corretamente
        setTimeout(function() {
            console.log('Largura final:', progressBar.css('width'));
            console.log('Largura computada:', progressBar[0].style.width);
        }, 800);
    }
    
    // Efeitos de hover nas alternativas
    $('.list-group-item').hover(
        function() {
            $(this).addClass('hover-effect');
        },
        function() {
            $(this).removeClass('hover-effect');
        }
    );
    
    // Animação dos boxes de resultado
    $('.acertos-box, .erros-box').hover(
        function() {
            $(this).animate({
                scale: 1.05
            }, 200);
        },
        function() {
            $(this).animate({
                scale: 1
            }, 200);
        }
    );
    
    // Efeito de loading no botão de responder
    $('#resposta-form button[type="submit"]').on('click', function() {
        const $button = $(this);
        const originalText = $button.text();
        
        $button.prop('disabled', true)
               .html('<span class="spinner-border spinner-border-sm me-2"></span>Processando...');
        
        // Reabilita o botão após 3 segundos (caso não haja redirecionamento)
        setTimeout(function() {
            $button.prop('disabled', false).text(originalText);
        }, 3000);
    });
}); 