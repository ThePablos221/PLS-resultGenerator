from PIL import Image, ImageDraw, ImageFont
import random
from moviepy.editor import *
import io
import cv2
import numpy as np
import VisualLayer
import Movement
import time

imageResolution = None
grandPrix = None
positionColor = None

FPS = 60

#belka górna 1s
#wjazd wyniki interwał 0.1s
#wyjazd wyniki 10s interwał 0.1s
#belka górna 1s

def rounded_rectangle(self: ImageDraw, xy, corner_radius, fill=None, outline=None):
    upper_left_point = xy[0]
    bottom_right_point = xy[1]
    self.rectangle(
        [
            (upper_left_point[0], upper_left_point[1] + corner_radius),
            (bottom_right_point[0], bottom_right_point[1] - corner_radius)
        ],
        fill=fill,
        outline=outline
    )
    self.rectangle(
        [
            (upper_left_point[0] + corner_radius, upper_left_point[1]),
            (bottom_right_point[0] - corner_radius, bottom_right_point[1])
        ],
        fill=fill,
        outline=outline
    )
    self.pieslice([upper_left_point, (upper_left_point[0] + corner_radius * 2, upper_left_point[1] + corner_radius * 2)],
        180,
        270,
        fill=fill,
        outline=outline
    )
    self.pieslice([(bottom_right_point[0] - corner_radius * 2, bottom_right_point[1] - corner_radius * 2), bottom_right_point],
        0,
        90,
        fill=fill,
        outline=outline
    )
    self.pieslice([(upper_left_point[0], bottom_right_point[1] - corner_radius * 2), (upper_left_point[0] + corner_radius * 2, bottom_right_point[1])],
        90,
        180,
        fill=fill,
        outline=outline
    )
    self.pieslice([(bottom_right_point[0] - corner_radius * 2, upper_left_point[1]), (bottom_right_point[0], upper_left_point[1] + corner_radius * 2)],
        270,
        360,
        fill=fill,
        outline=outline
    )

def setup():
    global imageResolution, grandPrix, positionColor
    imageResolution = (1920, 1080)
    grandPrix = "ROLEX Hungarian Grand Prix 09.05.2019 20:00"
    positionColor = (30,30,30)

def convertTime(time):
    hours = 0
    minutes = 0
    while (time > 3600):
        time -= 3600
        hours += 1
    while (time > 60):
        time -= 60
        minutes += 1

    res = ""
    if hours > 0:
        if hours < 10:
            res += "0"
        res += str(hours) + ":"
    if minutes > 0:
        if minutes < 10 and res != "":
            res += "0"
        res += str(minutes) + ":"
    if time < 10 and res != "":
        res += "0"
    res += '{:.3f}'.format(round(time, 3))
    return res

def generateResults():
    results = [] # imie zespol okr czas strata
    leaderTime = random.uniform(80, 85)
    previousTime = leaderTime
    time = previousTime
    for x in range(0, random.randint(12, 24)):
        results.append(["Kierowca " + str(x + 1), 
                        "Zespol XYZ", str(random.randint(15, 60)), 
                        convertTime(time), 
                        "+" + convertTime(time - previousTime), 
                        "+" + convertTime(time - leaderTime)])
        previousTime = time
        time += random.uniform(0.001, 0.5)
    return results

def drawPositionBox(draw: ImageDraw, position, row, positionFont, resultFont):
    global positionColor
    if position == 0:
        positionColor = (206, 47, 47)

    draw.rectangle([(50, 200 + position * 83), (50 + 70, 200 + 70 + position * 83)], positionColor)
    draw.rectangle([(50 + 70 + 13, 200 + position * 83), (imageResolution[0] - 50, 200 + 70 + position * 83)], (30, 30, 30))
    w, h = draw.textsize(str(position + 1), positionFont)
    draw.text((50 + (70 - w) / 2, 200 + (70 - h) / 2 + position * 83 - 5), str(position + 1), 'white', positionFont)

    '''
    draw.rectangle([(150, 200 + x * 83), (150 + 400, 200 + 70 + x * 83)], (255, 0, 0)) #imie nazwisko
    draw.rectangle([(580, 200 + x * 83), (580 + 400, 200 + 70 + x * 83)], (0, 0, 255)) #zespol
    draw.rectangle([(1000, 200 + x * 83), (1100, 200 + 70 + x * 83)], (127, 0, 255)) #okr
    draw.rectangle([(1090, 200 + x * 83), (1350, 200 + 70 + x * 83)], (0, 127, 255)) #czas
    draw.rectangle([(1350, 200 + x * 83), (1610, 200 + 70 + x * 83)], (127, 127, 255)) #interwał
    draw.rectangle([(1610, 200 + x * 83), (1870, 200 + 70 + x * 83)], (255, 127, 255)) #strata
    '''
    
    w, h = draw.textsize(row[0], resultFont)
    draw.text((150, 200 + position * 83 + (70 - h) / 2 - 5), row[0], 'white', resultFont)
    draw.text((580, 200 + position * 83 + (70 - h) / 2 - 5), row[1], 'white', resultFont)
    draw.text((1000, 200 + position * 83 + (70 - h) / 2 - 5), row[2], 'white', resultFont)
    draw.text((1090, 200 + position * 83 + (70 - h) / 2 - 5), row[3], 'white', resultFont)
    draw.text((1350, 200 + position * 83 + (70 - h) / 2 - 5), row[4], 'white', resultFont)
    draw.text((1610, 200 + position * 83 + (70 - h) / 2 - 5), row[5], 'white', resultFont)

    setup()

def main():
    setup()
    layers = []
    for i in range(10):
        layers.append([])
    bg = cv2.imread("background.jpg")
    video = cv2.VideoWriter("test.mov", cv2.VideoWriter_fourcc(*"mp4v"), 60, imageResolution)

    duration = 0
    results = generateResults()

    l = VisualLayer.VisualLayer()
    l.setOrder(1).setStart(2 * FPS).setDuration(2 * FPS, 15 * FPS, 2 * FPS).setupText(grandPrix, (50, 50), (255, 255, 255), ImageFont.truetype("Roboto-Regular.ttf", 64)).setupBackground(((50, 50), (imageResolution[0] - 50, 150)), (30,30,30))
    layers[l.order - 1].append(l)

    for i in range(10):

        l = VisualLayer.VisualLayer()
        l.setOrder(3).setStart(3 * FPS + i * 6).setDuration(0.5 * FPS, 10 * FPS, 0.5 * FPS).setupBackground(((100, 200 + i * 83),(170, 270 + i * 83)), (30, 30, 30)).setupText(str(i + 1), (100, 200 + i * 83), 'white', ImageFont.truetype("Roboto-Regular.ttf", 48), [True, True]).addMovement((-50, 0), 0, l.duration[0])
        layers[l.order - 1].append(l)
        l = VisualLayer.VisualLayer()
        l.setOrder(3).setStart(3 * FPS + i * 6).setDuration(0.5 * FPS, 10 * FPS, 0.5 * FPS).setupBackground(((183, 200 + i * 83),(1920, 270 + i * 83)), (30, 30, 30)).addMovement((-50, 0), 0, l.duration[0])
        layers[l.order - 1].append(l)

        l = VisualLayer.VisualLayer()
        l.setOrder(2).setStart(3 * FPS + i * 6).setDuration(0.5 * FPS, 10 * FPS, 0.5 * FPS).setupText(results[i][0], (200, 200 + i * 83), (255, 255, 255), ImageFont.truetype("Roboto-Regular.ttf", 30)).addMovement((-50, 0), 0, l.duration[0])
        layers[l.order - 1].append(l)
        l = VisualLayer.VisualLayer()
        l.setOrder(2).setStart(3 * FPS + i * 6).setDuration(0.5 * FPS, 10 * FPS, 0.5 * FPS).setupText(results[i][1], (630, 200 + i * 83), (255, 255, 255), ImageFont.truetype("Roboto-Regular.ttf", 30)).addMovement((-50, 0), 0, l.duration[0])
        layers[l.order - 1].append(l)
        l = VisualLayer.VisualLayer()
        l.setOrder(2).setStart(3 * FPS + i * 6).setDuration(0.5 * FPS, 10 * FPS, 0.5 * FPS).setupText(results[i][2], (1050, 200 + i * 83), (255, 255, 255), ImageFont.truetype("Roboto-Regular.ttf", 30)).addMovement((-50, 0), 0, l.duration[0])
        layers[l.order - 1].append(l)
        l = VisualLayer.VisualLayer()
        l.setOrder(2).setStart(3 * FPS + i * 6).setDuration(0.5 * FPS, 10 * FPS, 0.5 * FPS).setupText(results[i][3], (1140, 200 + i * 83), (255, 255, 255), ImageFont.truetype("Roboto-Regular.ttf", 30)).addMovement((-50, 0), 0, l.duration[0])
        layers[l.order - 1].append(l)
        l = VisualLayer.VisualLayer()
        l.setOrder(2).setStart(3 * FPS + i * 6).setDuration(0.5 * FPS, 10 * FPS, 0.5 * FPS).setupText(results[i][4], (1400, 200 + i * 83), (255, 255, 255), ImageFont.truetype("Roboto-Regular.ttf", 30)).addMovement((-50, 0), 0, l.duration[0])
        layers[l.order - 1].append(l)
        l = VisualLayer.VisualLayer()
        l.setOrder(2).setStart(3 * FPS + i * 6).setDuration(0.5 * FPS, 10 * FPS, 0.5 * FPS).setupText(results[i][5], (1660, 200 + i * 83), (255, 255, 255), ImageFont.truetype("Roboto-Regular.ttf", 30)).addMovement((-50, 0), 0, l.duration[0])
        layers[l.order - 1].append(l)

    for l1 in layers[::-1]:
        for layer in l1:
            if duration < layer.sumTimes():
                duration = layer.sumTimes()

    for frame in range(int(duration)):
        current = bg.copy()
        print(frame)
        for l1 in layers[::-1]:
            for layer in l1:
                if frame > layer.start and frame < (layer.start + sum(layer.duration)):
                    current = layer.renderFrame(current, frame)
                    #l.renderFrame()
        video.write(current)


    cv2.destroyAllWindows()
    video.release()
    return

if __name__ == "__main__":
    start = time.time()
    main()
    print("EXECUTED IN " + str(time.time() - start))