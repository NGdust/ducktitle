import os, sys, subprocess, shlex, re
from subprocess import call


class getProbe:
    def __init__(self, file):
        self.file = file
        self.parametres = self.getProbeFile()

    def getProbeFile(self):
        cmnd = ['ffprobe', '-show_format', '-show_entries', 'stream=height,width', '-loglevel', 'quiet', self.file]
        p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return out.decode('utf-8').split('\n')

    def getParam(self):
        duration, height, width = '', '', ''
        for param in self.parametres:
            if 'duration' in param:
                duration = param.split('=')[1]
            if 'height' in param:
                height = param.split('=')[1]
            if 'width' in param:
                width = param.split('=')[1]

        resolution = f'{width},{height}'
        return float(duration), resolution

    def checkError(self, extensions):
        if self.parametres[0]:
            for param in self.parametres:
                # print(param)
                if 'size' in param:
                    if int(param.split('=')[1]) / (1024 ** 3) > 1:
                        raise Exception('A file larger than 1 GB')
                if 'format_name' in param:
                    format_name = param.split('=')[1].split(',')
                    if not (set(format_name) & set(extensions)):
                        raise Exception('Not the right file format')
            return False
        else:
            raise Exception('Not mediafile')
