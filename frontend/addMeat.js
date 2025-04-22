// ========== Dragging and Dropping Meat ==========
import { grillGridWidth, grillGridHeight, backendBaseURL } from './app.js';

function drag(event) {
    event.dataTransfer.setData("text/plain", event.target.id);
}
  
// Allow dropping on grill
function allowDrop(event) {
    event.preventDefault();
}
  
// When user drops meat on the grill
function drop(event) {
    event.preventDefault();
    
    const meatId = event.dataTransfer.getData("text/plain"); //e.g., "Beef_1", "Pork_2", etc
    
    // The visual size (in pixels) of the <div id="grill"> as it appears on the screen.
    const grillRect = document.getElementById('grill').getBoundingClientRect(); 

    const x = event.clientX - grillRect.left; 
    const y = event.clientY - grillRect.top;

    const scaledX = Math.floor((x / grillRect.width) * grillGridWidth);
    const scaledY = Math.floor((y / grillRect.height) * grillGridHeight);

    console.log(`Dropped meat: ${meatId} at screen (${x}, ${y}), scaled to grill (${scaledX}, ${scaledY})`);
  
    addMeatToGrill(meatId, scaledX, scaledY);  
}
  

// Send meat drop info to backend
async function addMeatToGrill(meatId, x, y) {
    try { 
        const response = await fetch(`${backendBaseURL}/add_meat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ meat_id: meatId, x: x, y: y })
        });
    
        const result = await response.json();
        console.log('Backend added meat:', result);

    } catch (error) {
        console.error('Error adding meat:', error);
    }
}
  

document.addEventListener('DOMContentLoaded', () => {
    const meatImages = document.querySelectorAll('#menu-grid img');
    meatImages.forEach(img => {
      img.addEventListener('dragstart', drag);
    });
  
    const grillArea = document.getElementById('grill-area');
    grillArea.addEventListener('dragover', allowDrop);
    grillArea.addEventListener('drop', drop);
  });