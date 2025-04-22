# 8-Bit BBQ Grill

A lightweight web-based BBQ simulation game where you grill pixelated meats, collect them at the perfect moment,

## Gameplay

- **Drag & Drop**: Pick meats and veggies from the menu and drag them onto the ASCII grill.
- **Cooking Simulation**: Meats cook over time - from raw, to perfect, to burnt if you wait too long.
- **Clip Mode**: 
  - Click the "Clip" button to enter clipping mode.
  - Collect as many cooked meats as you want!
  - Click "Clip" again to exit clipping mode.
- **Clear Grill**: Reset the grill anytime by pressing "Clear the Grill".

## Gameplay Preview
![Gameplay Preview](/gameplay/img2.png)

![Gameplay](/gameplay/gameplay.gif)

## How It Works
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: FastAPI (Python)
- **Image Processing**: PIL (Python Imaging Library)
- **ASCII Art Renderer**: Converts images into ASCII characters, colored to mimic pixel art.

## How To Run
### 1. Backend Setup

```bash
# Install required packages
pip install fastapi uvicorn pillow numpy sty requests opencv-python

# Start the backend server
uvicorn backend.main:app --reload
