import os
import subprocess
import sys

def list_non_h264(dir, extensions=[".mkv", ".avi", ".mp4", ".m4v"]):
    filenames = []
    for filename in os.listdir(dir):
        if os.path.splitext(filename)[1] not in extensions: continue
        file_path = dir + "/" + filename
        cmd=["ffprobe", "-i", file_path, "-v", "error", "-of", "default=noprint_wrappers=1:nokey=1", "-show_entries", "stream=codec_name"]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, _ = p.communicate()
        if p.returncode != 0:
            raise subprocess.CalledProcessError(p.returncode, p.args)
        codecs = stdout.decode("utf-8").split("\n")
        if "h264" in codecs: continue        
        filenames.append(filename)
    return filenames

def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y': return True
        if reply[0] == 'n': return False


dir="/media/plaiseek/2To Storage/Films"

print("Listing non h264 files in \"{}\"".format(dir))
filenames = list_non_h264(dir)
nb_files = len(filenames)
print("{} files found :".format(nb_files))
if nb_files == 0:
    sys.exit()

print("\n".join(filenames))
if not yes_or_no("Are you sure you want to delete ..."): 
    sys.exit()

cmd=["rm", "-v"] + [dir + "/" + filename for filename in filenames]
p = subprocess.Popen(cmd)
p.wait(3600)
if p.returncode != 0:
    raise subprocess.CalledProcessError(p.returncode, p.args)