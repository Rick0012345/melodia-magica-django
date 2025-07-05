$(document).ready(function() {
    // Efeito de scroll na navbar
    $(window).scroll(function() {
        if ($(this).scrollTop() > 50) {
            $('.navbar').addClass('scrolled');
        } else {
            $('.navbar').removeClass('scrolled');
        }
    });

    // Animação suave para os links da navbar
    $('.nav-link').hover(
        function() {
            $(this).css('transform', 'translateY(-2px)');
        },
        function() {
            $(this).css('transform', 'translateY(0)');
        }
    );

    // Efeito de clique suave apenas para âncoras internas
    $('.nav-link').click(function(e) {
        const href = $(this).attr('href');
        
        // Verifica se é uma âncora interna (começa com #)
        if (href && href.startsWith('#')) {
            e.preventDefault();
            const target = $(href);
            
            if (target.length) {
                $('html, body').animate({
                    scrollTop: target.offset().top - 80
                }, 800);
            }
        }
        // Para links externos, permite navegação normal
    });

    // Animação do logo ao carregar a página
    $('.logo').fadeIn(1000).addClass('animated');
    
    // Efeito de destaque no item ativo do menu
    $('.nav-link').each(function() {
        if (window.location.pathname === $(this).attr('href')) {
            $(this).addClass('active');
        }
    });

    // Toggle do menu mobile com animação
    $('.navbar-toggler').click(function() {
        $('.navbar-collapse').slideToggle(300);
    });

    // Fechar menu mobile ao clicar em um link
    $('.navbar-nav .nav-link').click(function() {
        if ($(window).width() < 992) {
            $('.navbar-collapse').slideUp(300);
        }
    });
});
