// document.addEventListener('DOMContentLoaded', () => {
//   const carousel = document.querySelector('.parent');
//   const cards = carousel.querySelectorAll('.card');
//   const cardCount = cards.length;
//   const radius = 250;
//   let angle = 0;
//   let rotationY = 0;
//   let animationId;

//   // Posiciona os cards com a ordem invertida
//   function positionCards() {
//     const reversedCards = Array.from(cards).reverse();
//     for (let i = 0; i < cardCount; i++) {
//       const cardAngle = (360 / cardCount) * i + angle;
//       reversedCards[i].style.transform = `rotateY(${cardAngle}deg) translateZ(${radius}px)`;
//     }
//   }

//   // Animação girando da direita para a esquerda
//   function animate() {
//     rotationY += 0.3; // Roda no sentido anti-horário
//     angle = rotationY;
//     positionCards();
//     animationId = requestAnimationFrame(animate);
//   }

//   // Iniciar animação
//   animate();

//   // Pausar ao passar o mouse
//   carousel.addEventListener('mouseenter', () => {
//     cancelAnimationFrame(animationId);
//   });

//   // Retomar ao sair o mouse
//   carousel.addEventListener('mouseleave', () => {
//     animate();
//   });
// });
