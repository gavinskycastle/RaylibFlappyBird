import pyray as pr
from os import path

pr.init_audio_device()

# Spritesheet function
def make_spritesheet(image, cols, rows):
    totalCellCount = cols * rows
    
    rect = pr.Rectangle(0, 0, image.width, image.height)
    w = int(rect.width / cols)
    h = int(rect.height / rows)
    
    cell_rects = list([pr.Rectangle(index % cols * w, int(index // cols) * h, w, h) for index in range(totalCellCount)])
    
    cells = []
    
    for cell_rect in cell_rects:
        image_copy = pr.image_copy(image)
        pr.image_crop(image_copy, cell_rect)
        cells.append(image_copy)
    
    return cells

def scale2x_no_smoothing(image_name): # A function that returns the image scaled 2x
    image = pr.load_image(path.join("images", image_name))
    pr.image_resize_nn(image, image.width*2, image.height*2)
    return image
    
# Importing and organizing images
background_day = scale2x_no_smoothing("background_day.png")
background_night = scale2x_no_smoothing("background_night.png")
backgrounds = [background_day, background_night]

bird_spritesheet_image = scale2x_no_smoothing("bird.png")
bird_spritesheet = make_spritesheet(bird_spritesheet_image, 3, 3)

bird_yellow = bird_spritesheet[:3]
bird_red = bird_spritesheet[3:6]
bird_blue = bird_spritesheet[6:]

ground = scale2x_no_smoothing("ground.png")

pipe_spritesheet_image = scale2x_no_smoothing("pipe.png")
pipe_spritesheet = make_spritesheet(pipe_spritesheet_image, 2, 1)

big_score_text_image = scale2x_no_smoothing("big_score_text.png")
big_score_text = make_spritesheet(big_score_text_image, 10, 1)

small_score_text_image = scale2x_no_smoothing("small_score_text.png")
small_score_text = make_spritesheet(small_score_text_image, 10, 1)

game_over = scale2x_no_smoothing("game_over.png")

results_sheet = scale2x_no_smoothing("results_sheet.png")

get_ready = scale2x_no_smoothing("get_ready.png")

medals_spritesheet_image = scale2x_no_smoothing("medals.png")
medals_spritesheet = make_spritesheet(medals_spritesheet_image, 4, 1)

play_button_image = scale2x_no_smoothing("play_button.png")

# Setting the window icon
icon = pr.load_image(path.join("images", "icon.png"))
secret_icon = pr.load_image(path.join("images", "secret_icon.png")) # Secret code ;)
pr.set_window_icon(icon)

# Importing sounds
die_sound = pr.load_sound(path.join("sounds", "die.ogg"))
hit_sound = pr.load_sound(path.join("sounds", "hit.ogg"))
point_sound = pr.load_sound(path.join("sounds", "point.ogg"))
swoosh_sound = pr.load_sound(path.join("sounds", "swoosh.ogg"))
wing_sound = pr.load_sound(path.join("sounds", "wing.ogg"))

if __name__ == "__main__":
    print("Incorrect script, please run main.py")