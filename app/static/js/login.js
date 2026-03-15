// Efeito de brilho que segue o mouse nos inputs
document.querySelectorAll('.input-wrapper').forEach(wrapper => {
    const input = wrapper.querySelector('input');
    const glow = wrapper.querySelector('.input-glow');
    
    wrapper.addEventListener('mousemove', (e) => {
        const rect = wrapper.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        glow.style.setProperty('--x', `${x}%`);
        glow.style.setProperty('--y', `${y}%`);
    });
});