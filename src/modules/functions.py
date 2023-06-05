import os, shutil, requests, zipfile, platform, subprocess, socket, string, random
from rcon.source import Client
from modules.logging import log

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

rconpasswd = randomword(6)

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

userrconhist = []
rconhist = []
def sendrcon(cmd, password, port = 3280, hist = False):
    if hist:
        userrconhist.reverse()
        userrconhist.append(cmd)
        userrconhist.reverse()
    else:
        rconhist.append(cmd)
    try:
        with Client(local_ip, port, passwd=password) as client:
            response = client.run(cmd)
        return response
    except Exception as e:
        return ""

import urllib.request

def getsystem():
    system = platform.system().lower()
    return system

def list_files_recursive(directory):
    files_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), directory)
            files_list.append(file_path)
    return files_list

def puresymlink(original, new):
    if not os.path.exists(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new))
    if getsystem() == "linux":
        os.symlink(original, new)
    elif getsystem() == "windows":
        fh = open("NUL","w")
        subprocess.Popen('mklink /H "%s" "%s"' % (new, original), shell=True, stdout = fh, stderr = fh)
        fh.close()

def get_all_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(os.path.relpath(file_path, directory))
    return file_list

def symlink(original, new):
    if os.path.exists(original):
        if not os.path.exists(os.path.dirname(new)):
            os.makedirs(os.path.dirname(new))

        #* if its a directory itterate through it and sylink every file
        if os.path.isdir(original):
            for file in list_files_recursive(original):
                puresymlink(original + file, new + file)
        else:
            puresymlink(original, new)
    else:
        log("symlink failed", original)

def read_patchfile(filepath):
    f = open(filepath, "r")
    data = f.read().strip().split("\n")
    f.close()
    newdata = []

    for line in data:
        line = line.strip()
        if line.startswith("//"): continue
        line = line.split("//")[0].strip()
        newdata.append(line.lower())

    operations = []
    for line in newdata:
        if line.startswith("replace:"):
            line = line.replace("replace:", "").strip()
            operation = line.split("|")
            operation[0] = bytes.fromhex(operation[0].strip().replace(" ", ""))
            operation[1] = bytes.fromhex(operation[1].strip().replace(" ", ""))
            operations.append(operation)
    
    return operations

def patch_with_patchfile(binarypath, patchfilepath):
    operations = read_patchfile(patchfilepath)
    f = open(binarypath, "rb")
    data = f.read()
    f.close()

    for op in operations:
        data = data.replace(op[0], op[1])
    
    f = open(binarypath, "wb")
    f.write(data)
    f.close()

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

#* we need a way to download the latest version of the goldberg emulator https://mr_goldberg.gitlab.io/
def downloadgoldberg(outputpath = "steam_api.dll"):
    downloadfolder = "pydowntemp"
    downloadPath = downloadfolder+"/goldberg.zip"
    
    if os.path.exists(downloadfolder):
        shutil.rmtree(downloadfolder)
        
    os.mkdir(downloadfolder)
    urllib.request.urlretrieve("https://gitlab.com/Mr_Goldberg/goldberg_emulator/uploads/2524331e488ec6399c396cf48bbe9903/Goldberg_Lan_Steam_Emu_v0.2.5.zip", downloadPath)
    
    if os.path.exists(downloadPath):
        log("file exist")

    with zipfile.ZipFile(downloadPath, 'r') as zip_ref:
        zip_ref.extractall(downloadfolder)
        
    if os.path.exists("steam_api.dll"):
        os.remove("steam_api.dll")
        
    shutil.copy(downloadfolder+"/steam_api.dll", outputpath)
    shutil.rmtree(downloadfolder)
