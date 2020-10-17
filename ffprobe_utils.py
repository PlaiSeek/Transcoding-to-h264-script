import os
import subprocess
import sys
import time

def parse_duration_min(duration_str):
    parts = duration_str.split(":")
    minutes = 0
    for i,part in enumerate(parts):
        minutes += float(part) * pow(60, 1-i)
    return minutes

def parse_size_go(size_str):
    convert = {"G":1,"M":1024,"K":1024*1024}
    parts = size_str.split(" ")
    if len(parts) < 2: return None
    gos = float(parts[0])
    return gos * convert[parts[1][0]]

class VideoFileInfos:
    def __init__(self):
        self.tags={}
        self.streams=[]
    def __str__(self): return "{tags:"+self.tags.__str__()+",streams:"+self.streams.__str__()+"}"
    def __repr__(self): return "{tags:"+self.tags.__str__()+",streams:"+self.streams.__str__()+"}"

def getInfos(file_path):
    cmd=['ffprobe', '-show_streams', '-show_format', '-pretty', '-loglevel', 'quiet', '-i', file_path]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", universal_newlines=True)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print(file_path)
        raise subprocess.CalledProcessError(p.returncode, p.args)
    infos=VideoFileInfos()
    obj = None
    for line in stdout.split('\n'):
        if line.startswith('[/'): continue
        if line.startswith('[STREAM]'): 
            obj = {}
            infos.streams.append(obj)
            continue
        if line.startswith('[FORMAT]'): 
            obj = infos.tags
            continue
        entry = line.split("=")
        if len(entry) < 2: continue
        obj[entry[0]] = entry[1]
    return infos



def list_low_quality(dir, go_per_hour, extensions=[".mkv", ".avi", ".mp4", ".m4v"]):
    filenames = []
    for filename in os.listdir(dir):
        if os.path.splitext(filename)[1] not in extensions: continue
        file_path = dir + "/" + filename
        infos=getInfos(file_path)
        if infos == None: continue
        gos = parse_size_go(infos.tags["size"])
        hours = parse_duration_min(infos.tags["duration"]) / 60.0
        if gos == None or hours == None: continue
        if gos / hours >= go_per_hour: continue
        print("{} {} : {}".format(gos, hours, gos/hours))
        filenames.append(filename)
    return filenames


dir="/media/plaiseek/2To Storage/Films"
filenames = list_low_quality(dir, 0.75)
for filename in filenames:
    print(filename)
print(len(filenames))
