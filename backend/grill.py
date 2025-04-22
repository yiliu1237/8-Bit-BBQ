from .converter import *
from .meat import *
import os
import time

#### "images/BBQGrill_C.png" 
#### bg_size -> (300, 300)
class GrillState:

    def __init__(self, bg_img, bg_size, fixed_slots):
        self.fixed_slots = fixed_slots
        self.occupied = set()
        self.masks = {}
        self.meats = []  # list of Meat objects
        self.placements = {} 

        ascii_bg_str = image_to_ascii(bg_img, size=bg_size, fix_scaling=False)

        self.grid = ascii_to_grid(ascii_bg_str)
        self.original_grid = [row[:] for row in self.grid]

        self.colors = [
            [tuple(pixel) for pixel in row]
            for row in np.array(Image.open(bg_img).resize(bg_size).convert("RGB"))
        ]

        # self.original_colors = self.colors ###  makes original_colors a reference to the same list
        self.original_colors = [row[:] for row in self.colors]
        self.grill_mask = get_image_mask(bg_img, size=bg_size)


    def update(self, delta_time):
        for i, meat in enumerate(self.meats):
            meat.update(delta_time)

            # Repaint meat onto the grill
            fg_h, fg_w = len(meat.fg_grid), len(meat.fg_grid[0])
            bg_h, bg_w = len(self.grid), len(self.grid[0])

            # Find the slot the meat is occupying
            chosen = list(self.masks.keys())[i]
            x0, y0 = self.placements[chosen]

            for y in range(fg_h):
                for x in range(fg_w):
                    if meat.fg_mask[y, x]:
                        bx, by = x + x0, y + y0
                        if 0 <= bx < bg_w and 0 <= by < bg_h: 
                            self.colors[by][bx] = meat.fg_colors[y][x]



    def add_meat(self, meat: Meat, position, applyRotation=True):
        self.meats.append(meat)

        # Choose nearest available fixed slot
        available_slots = [slot for slot in self.fixed_slots if slot not in self.occupied]
        if not available_slots:
            print("No available slots")
            return

        fg_grid, fg_colors, fg_mask = meat.fg_grid, meat.fg_colors, meat.fg_mask
        # if applyRotation:
        if False: 
            # apply random rotation
            angle = random.choice([0, 90, 180, 270]) ### bug for 270
            fg_grid, fg_colors, fg_mask = rotate_ascii_block(meat.fg_grid, meat.fg_colors, meat.fg_mask, angle)
            meat.fg_grid = fg_grid
            meat.fg_colors = fg_colors
            meat.fg_mask = fg_mask
            print(f"Meat added with {angle}° rotation")


        bg_h, bg_w = len(self.grid), len(self.grid[0])
        fg_h, fg_w = len(fg_grid), len(fg_grid[0]) ## use fg_grid instead of meat.fg_grid

        

        # Pick the closest
        cx, cy = position
        chosen = min(available_slots, key=lambda p: (p[0]-cx)**2 + (p[1]-cy)**2)
        self.occupied.add(chosen)

        x0 = chosen[0] - fg_w // 2
        y0 = chosen[1] - fg_h // 2

        self.placements[chosen] = (x0, y0)

        global_mask = np.zeros_like(self.grill_mask, dtype=bool)

        for y in range(fg_h):
            for x in range(fg_w):
                if fg_mask[y, x]:
                    bx, by = x + x0, y + y0
                    if 0 <= bx < bg_w and 0 <= by < bg_h:
                        if not self.grill_mask[by, bx]:
                            print("out of bounds")
                            continue

                        self.grid[by][bx] = fg_grid[y][x]
                        global_mask[by][bx] = True
                        self.colors[by][bx] = fg_colors[y][x]

        self.masks[chosen] = global_mask
        return chosen




    def remove_meat(self, slot: tuple[int, int]):
        if slot not in self.occupied:
            print("Slot is not occupied.")
            return

        mask = self.masks.get(slot)
        if mask is None:
            return

        # Reset all pixels in the mask to original grill appearance
        for y in range(len(mask)):
            for x in range(len(mask[0])):
                if mask[y][x]:
                    self.grid[y][x] = self.original_grid[y][x]     
                    self.colors[y][x] = self.original_colors[y][x] 

        index = list(self.masks.keys()).index(slot)
        self.meats.pop(index)

        self.occupied.remove(slot)
        del self.masks[slot]
        del self.placements[slot]


    def remove_all_meat(self):
        all_slots = list(self.placements.keys())
        for pos in all_slots:
            print(self.meats)
            print(self.placements)
            self.remove_meat(pos)

        


def main():
    grill_img = "images/BBQGrill_C.png"
    grill_size = (300, 300)
    meat_size = (50, 50)
    fixed_slots = [(100, 100), (200, 100), (150, 150), (100, 200), (200, 200)]


    # grill_size = (50, 50)
    # meat_size = (10, 10)
    # fixed_slots = [(12, 16), (24, 16), (36, 16), (12, 32), (24, 32)]

    a = 1.666667
    b = 1

    grill_size = (int(grill_size[0] * a), int(grill_size[1] * b))
    meat_size = (int(meat_size[0] * a), int(meat_size[1] * b))
    fixed_slots = [(int(x * a), int(y * b)) for (x, y) in fixed_slots]


    grill = GrillState(grill_img, grill_size, fixed_slots)

    beef = Meat("images/transparent_topdown/beef_1.png", meat_size, 10, "beef")
    chicken = Meat("images/transparent_topdown/chicken_1.png", meat_size, 8, "chicken")
    pork = Meat("images/transparent_topdown/pork_1.png", meat_size, 10, "pork") 

    chicken2 = Meat("images/transparent_topdown/chicken_2.png", meat_size, 8, "chicken")

    mushroom = Meat("images/transparent_topdown/mushroom.png", meat_size, 8, "mushroom")

    center = (grill_size[0] // 2, grill_size[1] // 2)
    slot1 = grill.add_meat(pork, center)
    print(f"pork placed at slot: {slot1}")

    slot2 = grill.add_meat(chicken, center)
    print(f"chicken placed at slot: {slot2}")

    slot3 = grill.add_meat(beef, center)
    print(f"beef placed at slot: {slot3}")

    slot4 = grill.add_meat(chicken2, center)
    print(f"chicken placed at slot: {slot4}")

    slot5 = grill.add_meat(mushroom, center)
    print(f"mushroom placed at slot: {slot5}")

    # center = (grill_size[0] // 2, grill_size[1] // 2)
    # slot2 = grill.add_meat(chicken, center)
    # print(f"Chicken placed at slot: {slot2}")

    # colored = ascii_to_colored_image(grill.grid, grill.colors)
    # colored.save("grill_with_meat.png")

    # # Remove chicken and save
    # print("Removing chicken at slot:", slot2)
    # grill.remove_meat(slot2)
    # cleared = ascii_to_colored_image(grill.grid, grill.colors)
    # cleared.save("grill_cleared_2.png")
    # print("Grill cleared (chicken removed) and image saved.")

    # # Remove beef and save
    # print("Removing beef at slot:", slot1)
    # grill.remove_meat(slot1)
    # cleared = ascii_to_colored_image(grill.grid, grill.colors)
    # cleared.save("grill_cleared_1.png")
    # print("Grill cleared (beef removed) and image saved.")


    os.makedirs("frames", exist_ok=True)
    total_time = 12  # Simulate 12 seconds (2 seconds beyond cooked)
    dt = 1           # 1-second steps

    for i in range(total_time + 1):
        print(f"Simulating t={i}s")
        grill.update(dt)

        frame = ascii_to_colored_image(grill.grid, grill.colors)
        frame.save(f"frames/frame_{i:02d}.png")
        print(f"Frame {i} saved, cook_level: {pork.cook_level:.2f}")

        time.sleep(0.05)  # Optional, simulate real-time pacing

    print("Done! Cooking frames saved in 'frames/' folder.")
    


if __name__ == "__main__":
    main()