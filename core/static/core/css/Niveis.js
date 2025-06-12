
document.addEventListener('DOMContentLoaded', () => {
  const carousel = document.querySelector('.parent');
  const cards = carousel.querySelectorAll('.card');
  const cardCount = cards.length;
  const radius = 250;  // distância do centro ao card
  let angle = 0;
  let rotationY = 0;
  let animationId;

  // Posicionar os cards em círculo 3D
  function positionCards() {
    for (let i = 0; i < cardCount; i++) {
      const cardAngle = (360 / cardCount) * i + angle;
      cards[i].style.transform = `rotateY(${cardAngle}deg) translateZ(${radius}px)`;
    }
  }

  // Animação rotativa
  function animate() {
    rotationY += 0.3;  // Velocidade de rotação (muda para ajustar)
    angle = rotationY;
    positionCards();
    animationId = requestAnimationFrame(animate);
  }

  // Inicia animação
  animate();

  // Pausar rotação ao passar mouse
  carousel.addEventListener('mouseenter', () => {
    cancelAnimationFrame(animationId);
  });

  // Retomar rotação ao sair mouse
  carousel.addEventListener('mouseleave', () => {
    animate();
  });
});








