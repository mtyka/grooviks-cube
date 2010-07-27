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
    duration = models.IntegerField()
    color_array = [ (0,0,0) ] * 54

    def set_swirly(self, time):
        random.seed(time)
        for i in range(0,54):
            self.color_array[i] = (random.random(), random.random(), random.random() )

    
    def render(self):
        json_object = [self.duration, self.color_array]
        return json.dumps(json_object)


class AnimationPacket():
    # Contains 0-n KeyFrames
    # array of keyframes.
    pass

