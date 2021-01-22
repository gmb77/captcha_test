import os
import cv2
import numpy

captcha_dir = "../train_set"
output_dir = "letters"


def read_image(image_path):
    return cv2.imread(image_path)


def save_image(image_path, image):
    cv2.imwrite(image_path, image)


def preprocess_image(image):
    # convert to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # initialize border removing
    ind = 0
    start = (0, 0)
    # calculate first non-border colour of lower-left diagonal
    while image[ind, ind] == image[start]:
        ind += 1
    colour = int(image[ind, ind])
    h, w = image.shape[:2]
    mask = numpy.zeros((h + 2, w + 2), numpy.uint8)
    # replace border with background colour
    cv2.floodFill(image, mask, start, colour)
    # remove noise
    image = cv2.medianBlur(image, 3)
    image |= cv2.medianBlur(image, 3)
    # convert to black and white (binary) image
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # create border for crop
    border = 5
    return cv2.copyMakeBorder(image, border, border, border, border, cv2.BORDER_REPLICATE)


def find_regions(image, expected_char_num):
    # find continuous blocks (letters)
    contours = cv2.findContours(cv2.bitwise_not(image), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    min_size = 10
    char_regions = []
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if w > min_size and h > min_size:
            # split wide regions (estimating it contains two letters)
            if w / h > 1.25:
                half_width = int(w / 2)
                char_regions.append((x, y, half_width, h))
                char_regions.append((x + half_width, y, half_width, h))
            else:
                char_regions.append((x, y, w, h))

    char_regions = sorted(char_regions, key=lambda elem: elem[0])
    return char_regions if len(char_regions) == expected_char_num else []


def extract_letter(image, crop_rectangle):
    x, y, w, h = crop_rectangle
    return image[y - 2:y + h + 2, x - 2:x + w + 2]


counts = {}
for captcha in os.listdir(captcha_dir):
    filename = os.path.basename(captcha)
    captcha_word = os.path.splitext(filename)[0]
    img = read_image(os.path.join(captcha_dir, captcha))
    img = preprocess_image(img)
    regions = find_regions(img, len(captcha_word))
    ind = 0
    for region in regions:
        char = captcha_word[ind]
        char_dir = os.path.join(output_dir, char)
        if not os.path.exists(char_dir):
            os.makedirs(char_dir)
        letter = extract_letter(img, region)
        count = counts.get(char, 1)
        save_image(os.path.join(char_dir, "{}.png".format(str(count).zfill(4))), letter)
        counts[char] = count + 1
        ind += 1
