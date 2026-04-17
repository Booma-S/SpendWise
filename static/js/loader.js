// particles
const pc = document.getElementById('particles');
const cols = ['#c9a84c','#e8c76a','#8a6f2e','#6b5ba4','#9b8cc4'];

for (let i = 0; i < 28; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.cssText = `
        left: ${Math.random() * 100}%;
        width: ${Math.random() * 2 + 1}px;
        height: ${Math.random() * 2 + 1}px;
        background: ${cols[Math.floor(Math.random() * cols.length)]};
        animation-duration: ${Math.random() * 8 + 6}s;
        animation-delay: ${Math.random() * 5}s;
    `;
    pc.appendChild(p);
}

// progress
const msgs = document.querySelectorAll('.status-msg');
const fill = document.getElementById('progressFill');
const pct  = document.getElementById('pctLabel');

const steps = [
    { msg: 0, pct: 12 },
    { msg: 1, pct: 35 },
    { msg: 2, pct: 60 },
    { msg: 3, pct: 82 },
    { msg: 4, pct: 100 },
];

const delays = [400, 1200, 2000, 2800, 3600];

steps.forEach((step, i) => {
    setTimeout(() => {
        msgs.forEach(m => m.classList.remove('active'));
        msgs[step.msg].classList.add('active');
        fill.style.width = step.pct + '%';
        pct.textContent = step.pct + '%';
    }, delays[i]);
});