document.addEventListener('DOMContentLoaded', () => {
    const ball = document.getElementById('assistant-ball');
    const panel = document.getElementById('assistant-panel');
    
    if (!ball || !panel) return;

    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;
    
    // Check local storage for previous position
    const savedPos = localStorage.getItem('assistantPos');
    if (savedPos) {
        const pos = JSON.parse(savedPos);
        xOffset = pos.x;
        yOffset = pos.y;
        setTranslate(xOffset, yOffset, ball);
    }

    ball.addEventListener("mousedown", dragStart);
    document.addEventListener("mouseup", dragEnd);
    document.addEventListener("mousemove", drag);

    function dragStart(e) {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        
        if (e.target === ball) {
            isDragging = true;
        }
    }

    function dragEnd(e) {
        if (!isDragging) {
            // If it was just a click (no drag), toggle the panel
            if (e.target === ball) {
                if (panel.style.display === 'block') {
                    panel.style.display = 'none';
                } else {
                    panel.style.display = 'block';
                }
            }
        } else {
            initialX = currentX;
            initialY = currentY;
            isDragging = false;
            
            // Save position
            localStorage.setItem('assistantPos', JSON.stringify({x: xOffset, y: yOffset}));
        }
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;

            xOffset = currentX;
            yOffset = currentY;

            setTranslate(currentX, currentY, ball);
        }
    }

    function setTranslate(xPos, yPos, el) {
        el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
    }
});
