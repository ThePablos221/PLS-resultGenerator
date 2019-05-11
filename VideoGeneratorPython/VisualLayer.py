from PIL import Image, ImageDraw, ImageFont
import Movement
import cv2
import numpy as np
from copy import deepcopy

class VisualLayer(object):

    order = 0
    start = 0.0
    duration = [0,0,0] #fadein, keep, fadeout
    backgroundPosition = ((0,0), (0,0))
    backgroundColor = (0,0,0)
    backgroundRender = False
    text = ""
    textPosition = (0,0)
    textColor = (0,0,0)
    textRender = False
    textCenter = [False, False]
    font = ImageFont.truetype("Roboto-Regular.ttf", 30)
    movements = []

    def __init__(self):
        self.order = 0
        self.start = 0.0
        self.duration = [0,0,0] #fadein, keep, fadeout
        self.backgroundPosition = ((0,0), (0,0))
        self.backgroundColor = (0,0,0)
        self.backgroundRender = False
        self.text = ""
        self.textPosition = (0,0)
        self.textColor = (0,0,0)
        self.textRender = False
        self.textCenter = [False, False]
        self.font = ImageFont.truetype("Roboto-Regular.ttf", 30)
        self.movements = []

    def setOrder(self, value):
        self.order = value
        return self

    def setStart(self, frame):
        self.start = frame
        return self

    def setDuration(self, fadein, keep, fadeout):
        self.duration = [fadein, keep, fadeout]
        return self

    def setupText(self, text, xy, color, font, center = [False, False]):
        self.textRender = True
        self.textPosition = xy
        self.text = text
        self.textColor = color
        self.font = font
        self.textCenter = center
        return self

    def setupBackground(self, xy, color):
        self.backgroundRender = True
        self.backgroundColor = color
        self.backgroundPosition = xy
        return self

    def addMovement(self, vector, start, duration):
        obj = Movement.Movement(vector, start, duration)
        self.movements.append(obj)
        return self

    def renderFrame(self, image, frame):
        dt = frame - self.start
        #print(self.start, frame, dt, dt / 60, (dt - self.duration[0] - self.duration[1]) / self.duration[2])
        #print(self.text)

        drawable = image.copy()

        img = Image.fromarray(drawable)
        draw = ImageDraw.Draw(img)

        finalBgPosition = deepcopy(self.backgroundPosition)
        finalTextPosition = deepcopy(self.textPosition)
        for move in self.movements:
            if dt >= move.start and dt <= move.start + move.duration:
                #print(finalBgPosition[0][0], move.duration + move.start - dt, (move.duration + move.start - dt) / move.duration, move.vector[0], (move.duration + move.start - dt) / move.duration * move.vector[0], (1 - (move.duration + move.start - dt) / move.duration) * move.vector[0])
                finalBgPosition = (
                    (
                        finalBgPosition[0][0] + (1 - (move.duration + move.start - dt) / move.duration) * move.vector[0], 
                        finalBgPosition[0][1] + (1 - (move.duration + move.start - dt) / move.duration) * move.vector[1]
                    ), 
                    (
                        finalBgPosition[1][0] + (1 - (move.duration + move.start - dt) / move.duration) * move.vector[0],
                        finalBgPosition[1][1] + (1 - (move.duration + move.start - dt) / move.duration) * move.vector[1]
                    )
                )
                finalTextPosition = (
                    finalTextPosition[0] + (1 - (move.duration + move.start - dt) / move.duration) * move.vector[0],
                    finalTextPosition[1] + (1 - (move.duration + move.start - dt) / move.duration) * move.vector[1]
                )
            if dt < move.start:
                finalBgPosition = ((finalBgPosition[0][0], finalBgPosition[0][1]), (finalBgPosition[1][0], finalBgPosition[1][1]))
                finalTextPosition = (finalTextPosition[0], finalTextPosition[1])
            if dt > move.start + move.duration:
                finalBgPosition = ((finalBgPosition[0][0] + move.vector[0], finalBgPosition[0][1] + move.vector[1]), (finalBgPosition[1][0] + move.vector[0], finalBgPosition[1][1] + + move.vector[1]))
                finalTextPosition = (finalTextPosition[0] + move.vector[0], finalTextPosition[1] + move.vector[1])

        if self.backgroundRender:
            draw.rectangle(finalBgPosition, self.backgroundColor)
        #if self.textRender:
        w, h = draw.textsize(self.text, self.font)
        if self.textCenter[0] == True:
            finalTextPosition = (finalTextPosition[0] + (70 - w) / 2, finalTextPosition[1])
        if self.textCenter[1] == True:
            finalTextPosition = (finalTextPosition[0], finalTextPosition[1] + (70 - h) / 2)
        draw.text(finalTextPosition, self.text, self.textColor, self.font)
        drawable = np.array(img)
        #self.textCenter = [False, False]

        if dt < self.duration[0]:
            drawable = cv2.addWeighted(image, 1 - dt / self.duration[0], drawable, dt / self.duration[0], 0.0)
        if dt > self.duration[0] + self.duration[1]:
            drawable = cv2.addWeighted(image, (dt - self.duration[0] - self.duration[1]) / self.duration[2], drawable, 1 - (dt - self.duration[0] - self.duration[1]) / self.duration[2], 0.0)

        return drawable

    def sumTimes(self):
        return self.start + sum(self.duration)