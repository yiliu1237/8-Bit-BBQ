from .converter import *

class Meat:
    COOK_TARGETS = {
        "beef": {
            "light": (240, 200, 100),  # for bright spots (like fat parts)
            "dark": (186, 125, 77),     # for raw reddish parts
            "overcooked_light": (24, 24, 24),
            "overcooked_dark": (60, 55, 30)
        },
        "chicken": {
            "light": (255, 163, 49),
            "dark": (255, 163, 49),
            "overcooked_light": (86, 69, 44),
            "overcooked_dark" : (86, 69, 44)
        },
        "pork": {
            "light": (240, 200, 100),
            "dark": (220, 200, 175),
            "overcooked_light": (24, 24, 24),
            "overcooked_dark": (153, 106, 61)
        }, 
        "mushroom": {
            "light": (243, 218, 155),
            "dark": (243, 218, 155),
            "overcooked_light": (88, 56, 35),
            "overcooked_dark": (88, 56, 35)
        },
        "eggplant": {
            "light": (220, 170, 93),
            "dark": (220, 170, 93),
            "overcooked_light": (117, 42, 35),
            "overcooked_dark": (117, 42, 35)
        },
        "potato":{
            "light": (253, 216, 92),
            "dark": (253, 216, 92),
            "overcooked_light": (58, 52, 40),
            "overcooked_dark": (58, 52, 40)
        }

    }


    def __init__(self, fg_img, fg_size, cook_duration, meat_type):
        self.image_path = fg_img
        self.meat_type = meat_type
        self.raw_image = Image.open(fg_img).convert("RGBA")
        self.size = fg_size  
        self.cook_level = 0.0  # 0.0 = raw, 0.8 = well done, 1.0 = over-cooked
        self.cook_duration = cook_duration  # seconds to cook fully

        ascii_fg_str = image_to_ascii(fg_img, size=fg_size, fix_scaling=False)
        self.fg_grid = ascii_to_grid(ascii_fg_str)
        self.fg_mask = get_image_mask(fg_img, size=fg_size)
        self.is_done = False

        self.fg_colors = [
            [tuple(pixel) for pixel in row]
            for row in np.array(Image.open(fg_img).resize(fg_size).convert("RGB"))
        ]

        self.original_colors = [element for element in self.fg_colors]



    def update(self, delta_time):
        if not self.is_done:
            self.cook_level = min(1.0, self.cook_level + delta_time / self.cook_duration)
            self.cook_colors()
            if self.cook_level >= 1.0:
                self.is_done = True


    # the function is called every frame
    def cook_colors(self):
        new_colors = []

        row_count = 0
        for row in self.original_colors:
            new_row = []
            pixel_count = 0

            for r, g, b in row: # equal to (for pixel in row: r, g, b = pixel)
                
                #it might overflow silently when r + g + b > 255 — for example, (255 + 255 + 255) = 765, but uint8 wraps around after 255.
                brightness = (int(r) + int(g) + int(b)) / 3.0

                if self.cook_level <= 0.8:
                    # 0 -> 0.8: warming up based on color type
                    t = self.cook_level / 0.8

                    if brightness > 200:
                        # white/pale - fat
                        target = Meat.COOK_TARGETS[self.meat_type]["light"]  
                    elif r > g and r > b:
                        # reddish (likely raw meat)
                        target = Meat.COOK_TARGETS[self.meat_type]["dark"]  
                    else:
                        target = [r, g, b]

                    cooked_r = int(r * (1 - t) + target[0] * t)
                    cooked_g = int(g * (1 - t) + target[1] * t)
                    cooked_b = int(b * (1 - t) + target[2] * t)

                else:
                    # 0.8 → 1.0: overcooking/charred
                    t = (self.cook_level - 0.8) / 0.2

                    if brightness > 200:
                        target = Meat.COOK_TARGETS[self.meat_type]["overcooked_light"]  
                    elif r > g and r > b:
                        target = Meat.COOK_TARGETS[self.meat_type]["overcooked_dark"]  
                    else:
                        target = [r, g, b]

                    cooked_r = int(self.fg_colors[row_count][pixel_count][0] * (1 - t) + target[0] * t)
                    cooked_g = int(self.fg_colors[row_count][pixel_count][1] * (1 - t) + target[1] * t)
                    cooked_b = int(self.fg_colors[row_count][pixel_count][2] * (1 - t) + target[2] * t)

                new_row.append((cooked_r, cooked_g, cooked_b))
                pixel_count += 1
            
            new_colors.append(new_row)
            row_count += 1

        self.fg_colors = new_colors
    
