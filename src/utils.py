#!/usr/bin/python27

import subprocess

def alert():
    subprocess.call('./beep.sh'); 

def url_mode(opts):
    if opts.url != None:
        return True;

def ssh_mode(opts):
    if opts.ssh != False:
        return True;