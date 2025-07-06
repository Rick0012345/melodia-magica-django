// Isso da um tham no site
const particlesArray = [];

function createParticles() {
  const particle = {
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    size: Math.random() * 5 + 3,
    speedX: Math.random() * 1 - 0.5,
    speedY: Math.random() * 1 - 0.5,
    color: `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 0.8)`
  };
  particlesArray.push(particle);
}

function animateParticles() {
  const particleContainer = document.getElementById("particle-container");
  particleContainer.innerHTML = '';  // Limpar partículas anteriores

  particlesArray.forEach(p => {
    p.x += p.speedX;
    p.y += p.speedY;

    const particle = document.createElement("div");
    particle.style.position = "absolute";
    particle.style.borderRadius = "50%";
    particle.style.width = `${p.size}px`;
    particle.style.height = `${p.size}px`;
    particle.style.backgroundColor = p.color;
    particle.style.left = `${p.x - p.size / 2}px`;
    particle.style.top = `${p.y - p.size / 2}px`;

    particleContainer.appendChild(particle);
  });

  requestAnimationFrame(animateParticles);
}

setInterval(createParticles, 100); // Criar partículas constantemente
animateParticles();


