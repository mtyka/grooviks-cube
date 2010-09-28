import json
import random

from django.db import models

# Create your models here.

class Squares(models.Model):

    colors = models.CharField(max_length = 30)

    def render(self):
        return self.colors

    def __str__(self):
        return self.colors

    def rotate(self):
        self.colors = self.colors[1:] + self.colors[0]


class KeyFrame(models.Model):
    duration = models.IntegerField(null = True, default=100)
    color_array_string = models.TextField()

    def color_array(self):
        return json.loads(color_array_string)

    def set_swirly(self, time):
        random.seed(time)
        color_array = [0] * 54
        for i in range(0,54):
            color_array[i] = (random.random(), random.random(), random.random() )
        self.color_array_string = json.dumps(color_array)

    def render(self):
        return "[1,%s]" % self.color_array_string

    def __str__(self):
        return self.color_array_string[0:50]


class AnimationPacket():
    # Contains 0-n KeyFrames
    # array of keyframes.
    pass

