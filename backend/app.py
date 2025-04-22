from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .grill import GrillState
from .meat import Meat
from .converter import grid_to_ascii
import os

app = FastAPI()


# Allow frontend to call backend (important if on different ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up the Grill
grill_size = (300, 300)
meat_size = (50, 50)
fixed_slots = [(100, 100), (150, 80), (200, 100), (90, 150), (150, 150), (210, 150), (100, 200), (150, 210), (200, 200)]

a = 1.666667 / 3.
b = 1. / 3.

grill_size = (int(grill_size[0] * a), int(grill_size[1] * b))
meat_size = (int(meat_size[0] * a), int(meat_size[1] * b))
fixed_slots = [(int(x * a), int(y * b)) for (x, y) in fixed_slots]

center = (grill_size[0] // 2, grill_size[1] // 2)


grill_image_path = os.path.join("images", "BBQGrill_C.png")
grill = GrillState(bg_img=grill_image_path, bg_size=grill_size,
                   fixed_slots=fixed_slots)




@app.get("/get_ascii")
async def get_ascii():
    ascii_grid = grill.grid

    color_grid = [
        [ [int(r), int(g), int(b)] for (r,g,b) in row ]
        for row in grill.colors
    ]

    return JSONResponse(content={
        "ascii_grid": ascii_grid,
        "color_grid": color_grid
    })


@app.post("/update")
def update():
    try:
        grill.update(delta_time=1)
        return {"status": "updated"}
    except Exception as e:
        print(f"Update error: {e}")
        return {"status": "error", "detail": str(e)}


@app.post("/add_meat")
async def add_meat_endpoint(data: dict):
    meat_id = data["meat_id"]  # example: "Beef_1"
    x = data["x"]
    y = data["y"]

    meat_type = meat_id.split("_")[0].lower()  # "Beef_1" -> "beef"

    cook_times = {
        "beef": 50,
        "pork": 40,
        "chicken": 30,
        "potato": 20,
        "mushroom": 15,
        "eggplant": 20
    }

    if meat_type not in cook_times:
        return JSONResponse(content={"error": "Unknown meat type!"}, status_code=400)


    image_path = os.path.join("images", "transparent_topdown", meat_id.lower() + ".png")

    print(image_path)

    # Create the real Meat object
    meat = Meat(
        image_path,
        fg_size=meat_size,
        cook_duration=cook_times[meat_type],
        meat_type=meat_type
    )

    grill.add_meat(meat, position=(x, y))

    return {"message": "Meat added!"}




@app.post("/clip_meat")
async def clip_meat(data: dict):
    x = data["x"]
    y = data["y"]

    # check if grill has any meats
    if not grill.occupied:
        return {"success": False, "detail": "No meats on grill"}

    # Try to find a meat whose mask contains the clicked point
    found_slot = None
    for slot, mask in grill.masks.items():
        # Each mask is a 2D boolean grid
        if 0 <= int(y) < mask.shape[0] and 0 <= int(x) < mask.shape[1]:
            if mask[int(y), int(x)]:
                found_slot = slot
                break

    if found_slot is None:
        return {"success": False, "detail": "No meat at clicked location."}

    # If found, collect that meat
    meat_index = list(grill.masks.keys()).index(found_slot)
    collected_meat = grill.meats[meat_index]

    meat_type = collected_meat.meat_type
    cook_level = collected_meat.cook_level

    grill.remove_meat(found_slot)

    return {
        "success": True,
        "meat_type": meat_type,
        "cook_level": cook_level
    }



@app.post("/clear_grill")
async def clear_grill():
    try:
        grill.remove_all_meat()
        return {"status": "cleared"}
    except Exception as e:
        print(f"Clear grill error: {e}")
        return {"status": "error", "detail": str(e)}
