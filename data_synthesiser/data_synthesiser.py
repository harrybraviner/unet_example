import random
import numpy as np
from math import floor
from PIL import Image
from scipy.ndimage.interpolation import rotate

max_pixel_val = 255.0

def make_background(width, height, random_gen):
    return np.array([[random_gen() for x in range(width)] for y in range(height)])

def fuzzy_drawer():
    if (random.randrange(2) == 1):
        return random.uniform(0.0, max_pixel_val)
    else:
        return max_pixel_val

def make_background_fuzzy(width, height):
    return make_background(width, height, fuzzy_drawer)

def get_random_location(glyph, background):
    # The call to min is because the uniform function claim that uniform(a,b) can return b
    offset_x = min(floor(random.uniform(0.0, background.shape[1] - glyph.shape[1])), background.shape[1]-1)
    offset_y = min(floor(random.uniform(0.0, background.shape[0] - glyph.shape[0])), background.shape[0]-1)
    return (offset_x, offset_y)

def impose_glyph_on_background(glyph, background, location, impose_function):
    offset_x, offset_y = location
    # In-place imposition of the glyph on the background
    for x in range(glyph.shape[1]):
        for y in range(glyph.shape[0]):
            glyph_darkness = max_pixel_val - glyph[y,x]
            background_darkness = max_pixel_val - background[y,x]
            combined_darkness = min(max_pixel_val, glyph_darkness + background_darkness)
            background[y + offset_y, x + offset_x] = max_pixel_val - combined_darkness

def get_label(glyph, background, location):
    labels = np.zeros(background.shape)
    offset_x, offset_y = location
    for x in range(glyph.shape[1]):
        for y in range(glyph.shape[0]):
            if (glyph[y,x] != max_pixel_val):
                labels[y + offset_y, x + offset_x] = 1.0
    return labels

def impose_glyph_on_background_at_random_location(glyph, background, impose_function):
    location = get_random_location(glyph, background)
    impose_glyph_on_background(glyph, background, location, impose_function)

def impose_glyph_on_background_and_return_label(glyph, background, impose_function):
    location = get_random_location(glyph, background)
    impose_glyph_on_background(glyph, background, location, impose_function)
    return get_label(glyph, background, location)


def make_A_glyph():
    im = Image.open("letterA.png")
    return np.array([[im.getpixel((x,y))[0] for x in range(im.width)] for y in range(im.height)])

def fuzz_glyph(glyph, threshold=180, fuzzmin = 0.0, fuzzmax = 180.0):
    return np.array([[max_pixel_val if glyph[y,x] >= threshold else random.uniform(fuzzmin, fuzzmax) for x in range(glyph.shape[1])] for y in range(glyph.shape[0])])

def crop_glyph(glyph):
    minx = next(x for x in range(glyph.shape[1]) if any([i < max_pixel_val for i in glyph[:,x]]))
    miny = next(y for y in range(glyph.shape[0]) if any([i < max_pixel_val for i in glyph[y,:]]))
    maxx = next(x for x in reversed(range(glyph.shape[1])) if any([i < max_pixel_val for i in glyph[:,x]]))
    maxy = next(y for y in reversed(range(glyph.shape[0])) if any([i < max_pixel_val for i in glyph[y,:]]))
    return glyph[miny:(maxy+1), minx:(maxx+1)]

def rotate_fuzz_and_crop(glyph):
    angle = random.uniform(0.0, 360.0)
    rotated_glyph = rotate(glyph, angle = angle, cval = max_pixel_val, order = 0)
    return crop_glyph(fuzz_glyph(rotated_glyph))

# Started off using this - think it'll be a problem because 'A' areas will be darker
def impose_by_addition(glyph_brightness, background_brightness):
    glyph_darkness = max_pixel_val - glyph[y,x]
    background_darkness = max_pixel_val - background[y,x]
    combined_darkness = min(max_pixel_val, glyph_darkness + background_darkness)
    return max_pixel_val - combined_darkness

def impose_by_max_darkness(glyph_brightness, background_brightness):
    return min(glyph_brightness, background_brightness)

def make_fuzzy_image_and_label():
    rotated_glyph = rotate_fuzz_and_crop(make_A_glyph())
    image = make_background_fuzzy(100, 100)
    label = impose_glyph_on_background_and_return_label(rotated_glyph, image, impose_by_max_darkness)
    return (image, label)
