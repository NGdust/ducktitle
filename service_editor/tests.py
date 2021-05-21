import os
import time
import unittest
from modules import calculator

class TestCalculator(unittest.TestCase):
    def setUp(self):
        resolution = list(map(int, '480,360'.split(',')))
        self.text = 'dbngfpQu'
        self.font = os.getcwd() + '/fonts/Arial.ttf'
        self.param = calculator.CalculatorParams(resolution, text=self.text, font=self.font)

    def test_getTailWord(self):
        tail = self.param._getTailWord()
        self.assertEqual(tail, 5)

    def test_getDimensions(self):
        dimensions = self.param._getDimensions(font=self.font, text=self.text)
        self.assertEqual(dimensions, (106, 24))

    def test_chunkIt(self):
        chunkIt = self.param._chunkIt()
        self.assertTrue(type(chunkIt) == list)
        self.assertTrue(len(chunkIt) == 1)

    def test_getHWBackground(self):
        dimensions = self.param._getDimensions(font=self.font, text=self.text)[0]
        chunkIt = self.param._chunkIt()
        h, w = self.param._getHWBackground(dimensions, chunkIt)
        self.assertEqual(int(h), 37)
        self.assertEqual(int(w), 126)

    def test_getXYBackground(self):
        dimensions = self.param._getDimensions(font=self.font, text=self.text)[0]
        chunkIt = self.param._chunkIt()
        h, w = self.param._getHWBackground(dimensions, chunkIt)
        x, y = self.param._getXYBackground(h, w)
        self.assertEqual((x, y), (177, 323.0))

    def test_getXYsub(self):
        dimensions = self.param._getDimensions(font=self.font, text=self.text)[0]
        chunkIt = self.param._chunkIt()
        h, w = self.param._getHWBackground(dimensions, chunkIt)
        xBg, yBg = self.param._getXYBackground(h, w)
        tail = self.param._getTailWord()
        x, y = self.param._getXYSubtitle(xBg, yBg, w, dimensions, tail*2)
        self.assertEqual((x, y), (187, 333.0))

    def test_calculateParam(self):
        arrayText, outParametrs, outBackgroundParametrs, checkWidthTextRelativeVideo = self.param.calculateParam()
        self.assertEqual(type(arrayText), list)
        self.assertEqual(type(outParametrs), list)
        self.assertEqual(type(outBackgroundParametrs), dict)
        self.assertEqual(type(checkWidthTextRelativeVideo), bool)


if __name__ == '__main__':
    unittest.main()