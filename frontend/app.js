const backendBaseURL = (location.hostname === "localhost") ? "http://localhost:8000" : "https://your-real-backend.com";


let grillGridWidth = 1;
let grillGridHeight = 1;

async function updateGrill() {
  try {
    await fetch(`${backendBaseURL}/update`, { method: 'POST' });
    const response = await fetch(`${backendBaseURL}/get_ascii`);
    const data = await response.json();

    const asciiGrid = data.ascii_grid;
    const colorGrid = data.color_grid;

    grillGridWidth = asciiGrid[0].length;
    grillGridHeight = asciiGrid.length;

    let html = "";

    for (let y = 0; y < asciiGrid.length; y++) {
      for (let x = 0; x < asciiGrid[y].length; x++) {
        const char = asciiGrid[y][x];
        const [r, g, b] = colorGrid[y][x];
        html += `<span style="color: rgb(${r},${g},${b})">${char}</span>`;
      }
      html += "<br>";
    }

    document.getElementById('grill').innerHTML = html;

  } catch (error) {
    console.error('Error updating grill:', error);
  }
}




document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('update-button').addEventListener('click', updateGrill);

    document.getElementById('clear-button').addEventListener('click', async () => {
        try {
            const response = await fetch(`${backendBaseURL}/clear_grill`, { method: 'POST' });
            const result = await response.json();
            console.log('Grill cleared:', result);
            await updateGrill();  // Refresh grill display after clearing
        } catch (error) {
            console.error('Error clearing grill:', error);
        }
    });
});




// Auto update every second
setInterval(updateGrill, 1000);

// First update
updateGrill();


export {grillGridWidth, grillGridHeight, backendBaseURL}




