import math
from copy import copy
from io import BytesIO

from PIL import ImageFont


class CalculatorParams:
    def __init__(self, resolution, text='', font='Arial', textSize=25, backgroundOpacity=0.4, fontOpacity=1,
                 fontColor='ffffff', backgroundColor='000000', verticalAlign=0, horizontalAlign='center',
                 fullLengthBackground=False, backgroundShapeSquare=True):


        self.resolution = resolution
        self.border = 90
        self.x_interval = 10
        self.y_interval = (textSize * 1.5 - textSize) // 2
        self.string_interval = 0

        self.text = text
        self.font = font
        self.textSize = textSize
        self.backgroundOpacity = backgroundOpacity
        self.fontOpacity = fontOpacity
        self.fontColor = fontColor
        self.backgroundColor = backgroundColor
        self.backgroundShapeSquare = backgroundShapeSquare
        verticalAlign = self.resolution[1] - ((verticalAlign/100) * self.resolution[1])
        self.verticalAlign = verticalAlign if verticalAlign > textSize else textSize
        self.horizontalAlign = horizontalAlign
        self.fullLengthBackground = fullLengthBackground
        self.outParametrs = []

        self.tailWord = self._getTailWord()

    def _getTailWord(self):
        min = self._getDimensions(font=self.font, text='a')[1]
        max = self._getDimensions(font=self.font, text='p')[1]
        return max-min

    # Получаем длину строки в пикселях
    def _getDimensions(self, font, text):
        file = open(font, "rb")
        bytes_font = BytesIO(file.read())
        font = ImageFont.truetype(bytes_font, self.textSize)
        size = font.getsize(text)
        return size


    # Разбиваем массив слов на равные части и сливаем каждую часть в одну строку
    def _chunkIt(self):
        array_text = []
        words = self.text.split(' ')
        line = ''
        testLine = ''
        for i in range(0, len(words)):
            testLine += words[i] + ' '
            deimensionsLine = self._getDimensions(font=self.font, text=testLine)
            if deimensionsLine[0] > self.resolution[0] - self.border*2:
                array_text.append(line.rstrip())
                testLine = words[i] + ' '
                line = ''
            else:
                line = testLine
        if testLine:
            line = testLine
            array_text.append(line.rstrip())
        return array_text

    # Получаем высоту и ширину BG
    def _getHWBackground(self, w_text, arrayText):
        # Высота BG = высота текста на двойной интервал
        h = self.textSize * len(arrayText) + self.y_interval * 2
        if len(arrayText) > 1:
            h += self.tailWord

        # Если Background надо сделать по максимальной ширене длинного слова
        if self.backgroundShapeSquare:
            maxW = w_text
            for word in arrayText:
                testW = self._getDimensions(font=self.font, text=word)
                if testW[0] > maxW:
                    maxW = testW[0]
            w = maxW + self.x_interval * 2
        else:
            w = w_text + self.x_interval * 2
        if self.fullLengthBackground:
            w = self.resolution[0]
        return h, w


    # Получаем координаты Background
    def _getXYBackground(self, h, w):
        yBackground = self.verticalAlign - self.textSize
        if yBackground + h >= self.resolution[1]:
            yBackground = self.resolution[1] - h

        xBackground = 0
        if self.horizontalAlign == 'center':
            xBackground = self.resolution[0] // 2 - w // 2
        elif self.horizontalAlign == 'left':
            xBackground = self.x_interval
        elif self.horizontalAlign == 'right':
            xBackground = self.resolution[0] - w - self.x_interval

        if self.fullLengthBackground:
            xBackground = 0
        return xBackground, yBackground

    # Получаем координаты subtitle
    def _getXYSubtitle(self, xBackground, yBackground, wBackground, w_text, stringInterval):
        xSubtitle = xBackground + wBackground // 2 - w_text//2
        ySubtitle = yBackground + stringInterval

        if self.fullLengthBackground:
            if self.horizontalAlign == 'center':
                xSubtitle = wBackground // 2 - w_text // 2
            elif self.horizontalAlign == 'left':
                xSubtitle = xBackground + self.x_interval
            elif self.horizontalAlign == 'right':
                xSubtitle = wBackground - w_text - self.x_interval

        return xSubtitle, ySubtitle

    def calculateParam(self):
        stringInterval = self.tailWord*2
        outParametrs = []
        outBackgroundParametrs = {
            'backgroundOpasity': self.backgroundOpacity,
            'backgroundColor': self.backgroundColor,
        }
        arrayText = self._chunkIt()
        for item in arrayText:
            deimensionsItem = self._getDimensions(font=self.font, text=item)
            parametrs = {
                'text': item,
                'font': self.font,
                'fontOpasity': self.fontOpacity,
                'textSize': self.textSize,
                'fontColor': self.fontColor,
            }

            outBackgroundParametrs['h'], outBackgroundParametrs['w'] = self._getHWBackground(deimensionsItem[0], arrayText)
            outBackgroundParametrs['x_bg'], outBackgroundParametrs['y_bg'] = self._getXYBackground(outBackgroundParametrs['h'], outBackgroundParametrs['w'])
            parametrs['x_sub'], parametrs['y_sub'] = self._getXYSubtitle(outBackgroundParametrs['x_bg'], outBackgroundParametrs['y_bg'], outBackgroundParametrs['w'],
                                                              deimensionsItem[0], stringInterval)

            outParametrs.append(parametrs)
            # Увеличиваем межстрочный интервал на высоту титра
            stringInterval += self.textSize
        return arrayText, outParametrs, outBackgroundParametrs, self._checkWidthTextRelativeVideo(arrayText)

    def _checkWidthTextRelativeVideo(self, array_text):
        for item in array_text:
            deimensionsItem = self._getDimensions(font=self.font, text=item)
            if deimensionsItem[0] > self.resolution[0]:
                return True
        return False

    def getParametrs(self):
        array_text, outParametrs, outBackgroundParametrs, w = self.calculateParam()
        while outBackgroundParametrs['h'] > self.resolution[1] or w:
            self.textSize -= 1
            array_text, outParametrs, outBackgroundParametrs, w = self.calculateParam()
            if self.textSize == 1:
                break
        return outParametrs, outBackgroundParametrs
