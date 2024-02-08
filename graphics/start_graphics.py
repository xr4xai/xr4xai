# This file will be called from main.py. It will fork a new process, and then start the graphics loop in that process.
# A very big maybe really good to do is to maybe think about perhaps: switching this out with C/C++ code (specifically, 
# switching out graphics_loop.py with an actual executable). 
# Python system progaramming is, perhaps, the worst thing. Also right now, this almost definitely only works with Unix, or even just my Mac
# Just some things to think about.

import os
import sys

def child(fd_read):
    os.dup2(fd_read, 0) # dups over stdin 
    i = os.execv("/usr/local/bin/python3", ("python3", "graphics/graphics_loop.py",) )
    exit(1)


def parent():
    fd_read, fd_write = os.pipe()

    pid = os.fork()

    if pid == 0: # child process
        os.close(fd_write)
        child(fd_read)
        os._exit(0)
    else:        # parent
        os.close(fd_read)
        os.dup2(fd_write,1)
        #os.write(fd_write, G.encode())
        

if __name__ == "__main__":
    parent()
 
