import os
import subprocess
import sys
import time

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

progress_len = 0
def print_progress_bar(line):
    global progress_len
    line = line.split('\n')[0]
    sys.stdout.write("\b" * progress_len + " " * progress_len + "\b" * progress_len + line)
    progress_len = len(line)
    sys.stdout.flush()


preset_file="Jellyfin 1080p MKV x264.json"
in_dir="/media/plaiseek/2To Storage/Films"
out_dir="/media/plaiseek/2To Storage/Films x264"
out_extension=".mkv"

if not os.path.exists(out_dir):
    try: os.mkdir(out_dir)
    except OSError: print("Creation of the directory {} failed".format(out_dir))
    else: print("Successfully created the directory {}".format(out_dir))

print("Listing non h264 files in \"{}\"".format(in_dir))
filenames = ffprobe_utils.list_non_h264(in_dir)
nb_files = len(filenames)
print("{} files found".format(nb_files))

start_time = time.time()
print("Transcoding ...")
for i, filename in enumerate(filenames):
    in_file = in_dir + "/" + filename
    out_file = out_dir + "/" + os.path.splitext(filename)[0] + out_extension
    print("({}/{}) \"{}\"".format(i+1, nb_files, out_file))
    if os.path.exists(out_file): continue
    cmd=["HandBrakeCLI", "--preset-import-file", preset_file, "-a", "1,2,3", "-s", "1,2,3,4,5,6", "-i", in_file, "-o", out_file]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", universal_newlines=True)
    for stdout_line in iter(p.stdout.readline, ""):
        print_progress_bar(stdout_line)
    print_progress_bar("")
    p.wait(7200)
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)
    
end_time = time.time()
hours, rem = divmod(end_time-start_time, 3600)
minutes, seconds = divmod(rem, 60)
print("Completed in {:0>2} hours {:0>2} minutes and {:05.2f} seconds !".format(int(hours),int(minutes),seconds))
