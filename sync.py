#!/usr/bin/python

import os, subprocess, sys, time

def help():
    print(f'Usage: {sys.argv[0]} [OPTION]...')
    print(f'   or: {sys.argv[0]} [OPTION]... local remote local2 remote2 ...')
    print( 'Sync files between local and Android directory via ADB.')
    print( 'Specify each nested directory seperately.')
    print( 'No dir == use default sync dirs (hard code).')
    print()
    print( '	-v --adb	Print ADB output.')
    print( '	-q --quiet	Script be quiet.')
    exit(1)

AdbOut = False
Output = True

default_paths = [(, ), ("./source", "/storage/self/primary/dest")]
defaulti = 0

i = 0
args = sys.argv[1:]
if __name__ == '__main__':
    while len(args)-i > 0:
        arg = args.pop(i)
        if arg[0:1] == '-':
            if arg == '--':
                break

            if arg[1:2] != '-':
                if 'h' in arg:
                    exit(help())
                if 'q' in arg:
                    Output = False
                if 'v' in arg:
                    AdbOut = True

            if arg == '--help':
                exit(help())
            if arg == '--adb':
                Output = False
            if arg == '--verbose':
                AdbOut = True
        else:
            i+=1

if Output: print("-[ Sync music between device and computer ]-",file=sys.stderr)
print("If this hangs after you connect device, press kill script, and run sudo adb kill-server; sudo adb start-server",file=sys.stderr)
out = subprocess.run(("adb", "wait-for-device"), capture_output=not AdbOut)
if out.returncode != 0:
    if not AdbOut: print(str(out.stdout,encoding='utf-8'))
    print("^Error!")


def sync(lp, rp):
    print(lp,"<-->",rp)
    start  = time.time()
    local  = subprocess.getoutput("ls -A '{}'".format(lp)).split("\n")
    remote = subprocess.getoutput(f"adb shell 'ls -A \'{rp}\''").split("\n")
    push   = [f for f in local if f not in remote]
    pull   = [f for f in remote if f not in local and not f.find("minecraft")>-1]
    tot    = len(local)+len(remote)
    diff   = len(push)+len(pull)
    print(f"{tot} total files, {diff} different.")
    push=[lp+f for f in push]
    if len(push)>0:
        if Output: print("Pushing",len(push),"files to device...",file=sys.stderr)
        out = subprocess.run(("adb","push")+tuple(push)+(rp,), capture_output=not AdbOut)
        if Output and out.returncode == 0:
            print(f"{round(100*len(push)/diff,1)}% Done in {round(time.time()-start,1)} secs.",file=sys.stderr)
        if out.returncode != 0:
            if not AdbOut: print(str(out.stdout,encoding='utf-8'))
            print("^Error!")
    else:
        if Output: print("No files pushed.",file=sys.stderr)

    pull=[rp+f for f in pull]
    if len(pull)>0:
        if Output: print("Pulling", len(pull), "files from device...",file=sys.stderr)
        out = subprocess.run(("adb","pull")+tuple(pull)+(lp,), capture_output=not AdbOut)
        if Output and out.returncode == 0:
            print("100.0% Done in", round(time.time()-start,1), "secs.",file=sys.stderr)
        if out.returncode != 0:
            if not AdbOut: print(str(out.stdout,encoding='utf-8'))
            print("^Error!")
    else:
        if Output: print("No files pulled.",file=sys.stderr)
    return 0

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        while len(sys.argv) >= 3:
            lp, rp = sys.argv.pop(1), sys.argv.pop(1)
            if os.path.exists(lp) and subprocess.run(("adb","shell","[ -d "+rp+" ]")).returncode==0:
                out = sync(lp,rp)
                if out != 0: exit(out)
    else:
        while defaulti < len(default_paths):
            lp, rp = default_paths[defaulti]
            last = sync(lp, rp)!=0
            if last: break
            defaulti += 1
        exit(last)

