"""
Flappy Bird

© .GEARS Studios 2013
Port made by Gavin P
"""

# Importing libraries
import pyray as pr
import random
from os import path
from assets import *

# Setting up the window
screenw, screenh = 288, 512
fps = 60
pr.init_window(screenw, screenh, "Flappy Bird")
pr.set_target_fps(fps)
pr.set_window_icon(icon)

# TODO: add rotation
loaded_textures = {}
def blit(image, coords, rotation=0):
    global loaded_textures
    if image in loaded_textures:
        texture = loaded_textures[image]
    else:
        texture = pr.load_texture_from_image(image)
        loaded_textures.update({image: texture})
    
    pr.draw_texture(texture, int(coords[0]), int(coords[1]), pr.WHITE)
    
    return pr.Rectangle(coords[0], coords[1], image.width, image.height)

def collidelist(rect, rect_list):
    for l_rect in rect_list:
        if pr.check_collision_recs(rect, l_rect):
            return 1
    return -1

def collidepoint(point, rect):
    point_vector = pr.Vector2(int(point[0]), int(point[1]))
    return pr.check_collision_point_rec(point_vector, rect)

# Class for the bird that the player controls
class Bird:
    def __init__(self, starting_x, starting_y, images):
        self.x = self.starting_x = starting_x
        self.y = self.starting_y = starting_y
        self.images = images
        self.selected_images = self.select_images()
        self.selected_image_rotation = [0, 1, 2, 1]
        self.gravity = 5
        self.dead = False
        self.score = 0
        self.updates_since_death = 0
        
    def select_images(self): # Returns a random list of images from self.images to be displayed
        return random.choice(self.images)
        
    def jump(self): # Activates by pressing the space bar or up arrow key
        self.gravity = -5
        pr.play_sound(wing_sound)
        
    def update(self): # Checking for player input, updating the rect, and drawing the image accordingly
        global first_input

        # Moving the wing up and down
        if updates_since_launch % 4 == 0 and not self.gravity == 5: # This will be activated every 4 frames, or 15 times a second
            self.selected_image_rotation.append(self.selected_image_rotation.pop(0))
        
        # Decreasing velocity if the gravity is not back to normal, with a higher and faster level of gravity when dead
        if not self.dead:
            if self.gravity < 5:
                self.gravity += 0.2
        else:
            if self.gravity < 7.5:
                self.gravity += 0.4
        
        if not first_input: # Won't update gravity if the player has not tapped/clicked first
            self.gravity = 0
            rotation_amount = 0
        
        self.y += self.gravity # Implementing gravity
        
        if self.y < -5: # Disallowing the player's y to go off the screen, with a little bit of wiggle room
            self.y = -5
            self.gravity = 0
        
        if self.y > screenh-144: # Disallowing the player to move through the ground and killing them if they try to do so
            self.y = screenh-144
            if not self.dead:
                pr.play_sound(hit_sound)
            self.dead = True
            update_high_score()
        
        # Selecting the image to be blitted
        if self.gravity >= 5:
            blitted_image = self.selected_images[2] # Selected when the bird is hitting terminal velocity
        else:
            blitted_image = self.selected_images[self.selected_image_rotation[0]]
        # Calculating the amount the sprite should be rotated based on the gravity
        if self.gravity > 0:
            rotation_amount = (-self.gravity*15)+15
        else:
            rotation_amount = 15
        
        if not first_input: # Won't rotate the sprite if the player has not tapped/clicked first
            rotation_amount = 0
        
        
        bird_rect = pr.Rectangle(self.x+5, self.y+5, blitted_image.width-10, blitted_image.height-10) # Creating a rectangle for the bird, slightly shrunken to allow for some wiggle room
        pipe_rects = [pr.Rectangle(pipe[0], pipe[1], 52, 320) for pipe in pipes] # Creating a list of rectangles for the pipes
        pipe_right_edges = list(set([pipe[0]+52 for pipe in pipes])) # Creating a list of right edges of every pipe
        
        if not self.dead:
            # Killing the bird if it hits a pipe, and playing some sound effects
            if not collidelist(bird_rect, pipe_rects) == -1: 
                self.dead = True
                update_high_score()
                pr.play_sound(hit_sound)
            # Incrementing the bird's score when it passes the right edge of a set of pipes
            for pipe_edge in pipe_right_edges:
                if self.x == pipe_edge:
                    self.score += 1
                    pr.play_sound(point_sound)
        else:
            self.updates_since_death += 1
        
        if self.updates_since_death == fps/4:
            pr.play_sound(die_sound)
        
        blit(blitted_image, (self.x, self.y), rotation=rotation_amount) # Drawing the image to the screen

# Class for interactive menu buttons
class Button: 
    def __init__(self, x, y, texture):
        self.x = x
        self.y = y
        self.texture = texture
        self.blit_y = self.y
        self.pressed = False
    def update(self, when_clicked):
        # Gets rect from blitted surface
        self.rect = blit(self.texture, (self.x, self.blit_y))

        # Moves button slightly down when pressed, and launches function when released
        if collidepoint((pr.get_mouse_x(), pr.get_mouse_y()), self.rect):
            if pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT):
                self.pressed = True
                self.blit_y = self.y + 2
            elif self.pressed == True:
                self.pressed = False
                when_clicked()
                self.blit_y = self.y
                pr.play_sound(swoosh_sound)
        else:
            self.blit_y = self.y

def create_new_pipe(): # A function that adds a new set of pipes to the pipe list when called
    bottom_pipe_position = random.randrange(24+pipe_vertical_spacing, screenh-168)
    pipes.extend([
    [screenw+pipe_horizontal_spacing, bottom_pipe_position], 
    [screenw+pipe_horizontal_spacing, bottom_pipe_position-320-pipe_vertical_spacing]])

def score_text_surface(spritesheet, score, regular_width, one_width, height): # A function that inputs a number, a spritesheet, and various other values, and outputs a surface to be rendered to the screen
    score_digits = [int(digit) for digit in str(score)]
    score_surface = pr.gen_image_color(len(score_digits)*regular_width, height, pr.Color(0, 0, 0, 0))
    
    score_blit_x = 0
    
    for digit in score_digits:
        digit_image = spritesheet[digit]
        pr.image_draw(score_surface, digit_image, pr.Rectangle(score_blit_x, 0, digit_image.width, digit_image.height), pr.Rectangle(0, 0, score_surface.width, score_surface.height), pr.WHITE)
        if digit == 1:
            score_blit_x += one_width
        else:
            score_blit_x += regular_width
    
    # Cropping the score surface so it can be properly centered
    pr.image_alpha_crop(score_surface, 0)
     
    return score_surface

try:
    with open(path.join("save", "highscore"), "r") as file:
        high_score = int(file.read())
except:
    high_score = 0

pipe_vertical_spacing = 100 # The amount of pixels between the top pipes and the bottom pipes
pipe_horizontal_spacing = 100 # The amount of pixels between each set of pipes

play_fade_up = True # Whether we should fade to black or from black
play_fill_opacity = 0

play_button = Button(screenw/2-52, 300, play_button_image)

# Everything below this point should be reset when a new attempt is made
def start_game():
    global main_bird, ground_x, death_fill_opacity, play_fill_opacity, updates_since_launch, background, pipe_image, pipe_image_flipped, pipes, play_fade, first_input
    main_bird = Bird(70, screenh/2-12, [bird_yellow, bird_red, bird_blue]) # Creating the main bird, setting its starting position, and passing in it's selectable textures

    ground_x = 0

    death_fill_opacity = 255

    play_fade = True
    first_input = False

    updates_since_launch = 0 # A counter that increments every time pr.end_drawing() is called

    background = random.choice(backgrounds) # Selects a random background

    pipe_image = random.choice(pipe_spritesheet) # Randomly selects one of the pipe textures to be used
    pipe_image_flipped = pr.image_copy(pipe_image)
    pr.image_flip_vertical(pipe_image_flipped) # Creates flipped versions of the randomly selected pipe textures

    pipes = [] # A list containing the positions of every pipe in the game
start_game()

play_fade = False # Whether the fade to and from black should be played

# To pass into the button as the function to run
def reset_game():
    global play_fade, play_fill_opacity
    play_fade = True
    play_fill_opacity = 0

def update_high_score():
    global main_bird, high_score
    if main_bird.score > high_score:
        high_score = main_bird.score
        with open(path.join("save", "highscore"), "w") as file:
            file.write(str(high_score))

# Main loop
while not pr.window_should_close():
    pr.begin_drawing()
    
    # Event detection
    if pr.is_key_pressed(pr.KeyboardKey.KEY_SPACE) or pr.is_key_pressed(pr.KeyboardKey.KEY_UP): # Making the player jump when the space bar or up arrow key is pressed, if they aren't dead
        if not main_bird.dead:
            main_bird.jump()
            first_input = True
    if pr.is_key_pressed(pr.KeyboardKey.KEY_G):
        # Secret code ;)
        pr.set_window_icon(secret_icon)
        pr.set_window_title("Made by Gavin P")
    if pr.is_key_released(pr.KeyboardKey.KEY_G):
        pr.set_window_icon(icon)
        pr.set_window_title("Flappy Bird")
    if pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT):
        if not main_bird.dead:
            main_bird.jump()
            first_input = True
    pr.clear_background(pr.BLACK) # Filling the screen
    
    blit(background, (0, 0)) # Rendering the background
    
    if not pipes or max([pipe[0] for pipe in pipes]) < screenw-52:
        # Creating a new pipe if no pipes are present or none of the pipes are off the right side of the screen
        create_new_pipe()
    
    for pipe in pipes[:]: # Thanks so much user16038533 on StackOverflow for helping me with this! You'll probably never see this but just know you helped a lot :)
        if pipe[0] < -52: # Removes any pipes that are completely off the left side of the screen
            pipes.remove(pipe)
        else:
            if not main_bird.dead and first_input:
                pipe[0] -= 2 # Moving the pipes 2 pixels every frame
            if pipes.index(pipe) % 2: # Rendering every odd pipe normally, and every even pipe flipped
                blit(pipe_image_flipped, pipe)
            else:
                blit(pipe_image, pipe)
    
    blit(ground, (ground_x, screenh-112)) # Rendering the ground
    
    # Scrolling the ground
    if not main_bird.dead:
        if ground_x > -48:
            ground_x -= 2
        else:
            ground_x = 0
    
    main_bird.update() # Updating the bird

    # Rendering the big score
    if not main_bird.dead:
        big_score_surface = score_text_surface(big_score_text, main_bird.score, 24, 16, 36)
        blit(big_score_surface, (screenw/2-big_score_surface.width/2, 24))
    
    # Rendering the get ready screen
    if not first_input:
        blit(get_ready, (screenw/2-get_ready.width/2, screenh/2-get_ready.height/2))
    
    # Rendering the "game over" text and playing a swoosh sound effect
    if main_bird.updates_since_death >= fps*(3/4):
        blit(game_over, (screenw/2-96, 100))
        if main_bird.updates_since_death == fps*(3/4):
            pr.play_sound(swoosh_sound)
    
    if main_bird.updates_since_death >= fps*(6/4):
        # Rendering the results sheet and playing a swoosh sound effect
        blit(results_sheet, (screenw/2-113, 175))
        if main_bird.updates_since_death == fps*(8/4):
            pr.play_sound(swoosh_sound)
        # Rendering the small score text
        if main_bird.updates_since_death == fps*(6/4):
            small_score = 0
        small_score += 1
        if small_score > main_bird.score:
            small_score = main_bird.score
        small_score_surface = score_text_surface(small_score_text, small_score, 16, 12, 20)
        blit(small_score_surface, (screenw/2+91-small_score_surface.width, 209))
        # Rendering the small high score text
        small_high_score_surface = score_text_surface(small_score_text, high_score, 16, 12, 20)
        blit(small_high_score_surface, (screenw/2+91-small_high_score_surface.width, 250))
    
    # Rendering the medal and updating the play button
    if main_bird.updates_since_death >= fps*(8/4):
        if main_bird.score >= 10 and main_bird.score < 20:
            blit(medals_spritesheet[0], (screenw/2-87, 217))
        if main_bird.score >= 20 and main_bird.score < 30:
            blit(medals_spritesheet[1], (screenw/2-87, 217))
        if main_bird.score >= 30 and main_bird.score < 40:
            blit(medals_spritesheet[2], (screenw/2-87, 217))
        if main_bird.score >= 40:
            blit(medals_spritesheet[3], (screenw/2-87, 217))
        play_button.update(reset_game)
    
    if main_bird.dead: # Fading out the screen white when the player dies
        fill_surface = pr.gen_image_color(screenw, screenh, pr.Color(255, 255, 255, death_fill_opacity))
        blit(fill_surface, (0, 0))
        death_fill_opacity -= 16
        if death_fill_opacity < 0:
            death_fill_opacity = 0

    if play_fade: # Fading in and out the screen black when the game is played
        fill_surface = pr.gen_image_color(screenw, screenh, pr.Color(0, 0, 0, play_fill_opacity))
        blit(fill_surface, (0, 0))
        if play_fade_up:
            play_fill_opacity += 8
        else:
            play_fill_opacity -= 8
        if play_fill_opacity > 255:
            play_fill_opacity = 255
            play_fade_up = False
            start_game()
        if play_fill_opacity < 0:
            play_fill_opacity = 0
            play_fade = False
            play_fade_up = True
    
    updates_since_launch += 1
    
    pr.end_drawing() # Updating the screen

quit()