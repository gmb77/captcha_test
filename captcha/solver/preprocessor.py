import os
import cv2
import numpy

captcha_dir = "train_set"
output_dir = "letters"

counts = {}
for captcha in os.listdir(captcha_dir):
    filename = os.path.basename(captcha)
    captcha_word = os.path.splitext(filename)[0]
    # read captcha
    img = cv2.imread(os.path.join(captcha_dir, captcha))
    # convert to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # initialize border removing
    var = 0
    start = (0, 0)
    while img[var, var] == img[start]:
        var += 1
    colour = int(img[var, var])
    h, w = img.shape[:2]
    mask = numpy.zeros((h + 2, w + 2), numpy.uint8)
    # replace border with background colour (calculated as first non-border colour of lower-left diagonal)
    cv2.floodFill(img, mask, start, colour)
    # remove noise
    img = cv2.medianBlur(img, 3)
    img |= cv2.medianBlur(img, 3)
    # convert to black and white (binary)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # create border for crop
    var = 2
    img = cv2.copyMakeBorder(img, var, var, var, var, cv2.BORDER_REPLICATE)
    # finding continuous blocks (letters)
    contours = cv2.findContours(cv2.bitwise_not(img), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    var = 5
    char_images = []
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if w > var and h > var:
            if w / h > 1.25:
                half_width = int(w / 2)
                char_images.append((x, y, half_width, h))
                char_images.append((x + half_width, y, half_width, h))
            else:
                char_images.append((x, y, w, h))

    if len(char_images) != 4:
        continue

    char_images = sorted(char_images, key=lambda e: e[0])

    for char_rect, char in zip(char_images, captcha_word):
        char_dir = os.path.join(output_dir, char)
        if not os.path.exists(char_dir):
            os.makedirs(char_dir)
        # crop letter
        x, y, w, h = char_rect
        char_img = img[y - 2:y + h + 2, x - 2:x + w + 2]

        count = counts.get(char, 1)
        output_img = os.path.join(char_dir, "{}.png".format(str(count).zfill(4)))
        cv2.imwrite(output_img, char_img)

        counts[char] = count + 1
