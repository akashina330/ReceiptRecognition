import cv2
import numpy as np
import operator

def processImage(image):
    image1 = image.copy()
    gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(gray, 500, 60)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (100, 277))
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    cnts, hier = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    li = {}
    i = 0
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.0025 * peri, False)
        rect = cv2.minAreaRect(approx)
        area = int(rect[1][0] * rect[1][1])
        li.update({i: area})
        i = i + 1
        ki = sorted(li.items(), key=operator.itemgetter(1))
    c = cnts[ki[-1][0]]
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.0025 * peri, False)
    rect = cv2.minAreaRect(approx)
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    cv2.drawContours(image1, [box], 0, (0, 0, 255), 10)

    yy = int(box[2][1])
    yw = int(box[0][1])
    ww = int(box[1][0])
    wy = int(box[3][0])
    cut = image1[yy:yw, ww:wy]

    if cut.size == 0:
        return image
    else:
        return cut

