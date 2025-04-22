import { grillGridWidth, grillGridHeight, backendBaseURL } from './app.js';

let selectedSlot = null;
let isClipping = false; 

// When user clicks somewhere on the grill
document.getElementById('grill').addEventListener('click', async function(event) {
  if (!isClipping) {
    return; // Only clip if in clipping mode
  }

  const grillRect = this.getBoundingClientRect();
  const x = event.clientX - grillRect.left; 
  const y = event.clientY - grillRect.top;
  
  const scaledX = Math.floor((x / grillRect.width) * grillGridWidth);
  const scaledY = Math.floor((y / grillRect.height) * grillGridHeight);

  selectedSlot = { x: scaledX, y: scaledY };
  console.log('Selected slot for clipping:', selectedSlot);

  // Send to backend
  try {
    const response = await fetch(`${backendBaseURL}/clip_meat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(selectedSlot)
    });

    const result = await response.json();
    console.log('Collected meat info:', result);

    if (result.success) {
        if(result.cook_level > 0.8){
            alert(`Oh no, the ${result.meat_type} got overcooked...`);
        }
        else{
            alert(`Collected ${result.meat_type} cooked to ${Math.round(result.cook_level / 0.8 * 100)}%!`);
        }
      
    } else {
        alert('No meat at that location.');
    }

    selectedSlot = null;

  } catch (error) {
    console.error('Error clipping meat:', error);
  }

 // After clipping one meat, exit clip mode
//   document.body.classList.remove('clip-cursor');
//   isClipping = false; 
});

// When user clicks the "Clip" button
function clipSelectedMeat() {
    isClipping = !isClipping; // toggle clipping mode
  
    const clipButtonText = document.querySelector('#clip-button + .tool-text');
  
    if (isClipping) {
      document.body.classList.add('clip-cursor');
      if (clipButtonText) clipButtonText.textContent = "Exit Clip Mode";
      console.log("Clip mode activated! Click on grill to collect meat.");
    } else {
      document.body.classList.remove('clip-cursor');
      if (clipButtonText) clipButtonText.textContent = "Enter Clip Mode";
      console.log("Clip mode deactivated.");
    }
  }

document.addEventListener('DOMContentLoaded', () => {
    const clipButton = document.getElementById('clip-button');
    clipButton.addEventListener('click', clipSelectedMeat);
});

