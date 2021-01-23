import os
import cv2
import numpy

train_dirs = {
    "images": "../train_set",
    "output": "train_data/letters",
    "ignored": "train_data/ignored"
}
validation_dirs = {
    "images": "../validation_set",
    "output": "validation_data/letters",
    "ignored": "validation_data/ignored"
}


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


def find_regions(image):
    # find continuous blocks (letters)
    contours = cv2.findContours(cv2.bitwise_not(image), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    min_size = 10
    char_regions = []
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if max(w, h) > min_size:
            # split wide regions (estimating it contains two letters)
            # 1.4 is for M letters
            if w / h > 1.4:
                half_width = int(w / 2)
                char_regions.append((x, y, half_width, h))
                char_regions.append((x + half_width, y, half_width, h))
            else:
                char_regions.append((x, y, w, h))

    return sorted(char_regions, key=lambda elem: elem[0])


def crop_letter(image, crop_rectangle):
    x, y, w, h = crop_rectangle
    padding = 2
    return image[y - padding:y + h + padding, x - padding:x + w + padding]


def extract_letters(image_path, expected_char_num=None, ignored_dir=None):
    image = read_image(image_path)
    image = preprocess_image(image)
    regions = find_regions(image)
    filename = os.path.basename(image_path)
    if expected_char_num is None or expected_char_num < 0:
        expected_char_num = len(os.path.splitext(filename)[0])
    if len(regions) != expected_char_num:
        # print("Extraction of captcha " + filename + " was unsuccessful, it is ignored.")
        if ignored_dir is not None:
            ignored = os.path.abspath(ignored_dir)
            if not os.path.exists(ignored):
                os.makedirs(ignored)
            bad_image = image.copy()
            for (x, y, w, h) in regions:
                cv2.rectangle(bad_image, (x, y), (x + w, y + h), 128)
            save_image(os.path.join(ignored, filename), bad_image)
        return
    cropped_letters = []
    for region in regions:
        cropped_letters.append(crop_letter(image, region))
    return cropped_letters


def process_set(dataset):
    counts = {}
    for captcha in os.listdir(dataset["images"]):
        captcha_word = os.path.splitext(captcha)[0]
        letters = extract_letters(os.path.join(os.path.abspath(dataset["images"]), captcha), ignored_dir=dataset["ignored"])
        if letters is not None:
            for char, letter in zip(captcha_word, letters):
                char_dir = os.path.join(os.path.abspath(dataset["output"]), char)
                if not os.path.exists(char_dir):
                    os.makedirs(char_dir)
                count = counts.get(char, 1)
                save_image(os.path.join(char_dir, str(count).zfill(4) + ".png"), letter)
                counts[char] = count + 1


process_set(train_dirs)
process_set(validation_dirs)
