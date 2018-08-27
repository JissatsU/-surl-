#!/usr/bin/python27

import os, os.path
import sys
import re
import time 
import datetime
import multiprocessing
import subprocess 
import random 


class IP_MAN(multiprocessing.Process):

    def __init__(self, block_mode, block_perm, iface):
        multiprocessing.Process.__init__(self)
        self.HOSTS = {};                         # a dictonary that holds the ips and their access time intervals 
        self.READ_INT = 1;                       # time to wait before next log read 
        self.BLOCK_MODE = block_mode;            # a variable to enable | disable block mode 
        self.BLOCK_INT = 90;                     # time to wait before unblocking the connection 
        self.BLOCK_PERM = block_perm;            # a variable to enable | disable permanent connection blocking 
        self.BLOCKED_FILE = 'blocked.dat';       # a file that stores blocked ips 
        self.IFACE = iface;                      # the interface specified in the [ --iface ] option
    

    def run(self):
        while 1:
            time.sleep(self.READ_INT);
            self.store_hosts('all.dat');
            self.check_hosts_time(self.HOSTS);
            self.HOSTS = {};


    # Store each host with its time access intervals in [self.HOSTS]
    def store_hosts(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r+') as fp:
                contents = fp.readlines();
            fp.close();
            contents.reverse();

            for line in contents:
                ip = ((line.split('\n')[0].split(' - ')[1]).split(']:')[0])[1:];
                t_time = ((((line.split('\n')[0].split(' - ')[0]).split(' [')[1]).split(' ')[1])[:-1]);

                if ip in self.HOSTS:
                    self.HOSTS[ip].append(t_time);
                else:
                    self.HOSTS[ip] = [];
                    self.HOSTS[ip].append(t_time);


    # Check each host's last 3 access time intervals 
    # and if the time difference is <= 3sec [1 sec for each request] block the connection 
    def check_hosts_time(self, hosts):
        for host in hosts:
            if len(hosts[host]) >= 3:
                t = hosts[host][:3];
                now = ((datetime.datetime.now()).strftime('%H:%M')).split(':');
                to_sub = [ tt for tt in t if tt.split(':')[0] == now[0] and tt.split(':')[1] == now[1] ];
                if len(to_sub) == 3:
                    s1 = to_sub[0].split(':')[-1].split(',')[0];
                    s2 = to_sub[-1].split(':')[-1].split(',')[0];
                    if int(s1) - int(s2) < 3:
                        if self.is_blocked(host, self.BLOCKED_FILE):
                            pass;
                        else:
                            b = BLCK(host, self.BLOCK_PERM, self.BLOCK_INT, self.IFACE);
                            b.start();

    
    def is_blocked(self, ip, fp):
        if os.path.exists(fp):
            f = open(fp, 'r+');
            l = f.readlines();
            f.close();
            if ip+'\n' in l:
                return True;


# This class is responsible for the [all.dat] log file clearing 
# when it reaches N number of lines 
class FLUSHER(multiprocessing.Process):
    def __init__(self, log_lines):
        multiprocessing.Process.__init__(self)
        self.LOG_LINES = log_lines;

    def run(self):
        while 1:
            self.clear_all_dat('all.dat');
            time.sleep(1.2);
    
    def clear_all_dat(self, file):
        if os.path.exists(file):
            f = open(file, 'r+');
            nl = len(f.readlines());
            if int(nl) >= int(self.LOG_LINES):
                f.truncate(0);


# This class is responsible for the connection managing 
# block connection permanently if [ --block-perm ] option is set 
# block connection for 90sec if [ --block-perm ] option is not set 
class BLCK(multiprocessing.Process):
    def __init__(self, ip, blck_p, blck_i, iface):
        multiprocessing.Process.__init__(self)
        self.BLCK_PERM = blck_p;
        self.BLCK_INT = blck_i;
        self.IP = ip;
        self.IFACE = iface;

    def run(self):
        self.block(self.IP, self.IFACE);

    def block(self, ip, iface):
        if os.path.exists('blocked.dat'):
            m = 'a';
        else:
            m = 'w';
        f = open('blocked.dat', m);
        f.write(ip+'\n');
        f.close();
        subprocess.call(['./block.sh', ip, iface]);

        if self.BLCK_PERM == True:
            # do nothing [connection stays blocked]
            pass; 
        else:
            time.sleep(self.BLCK_INT);
            subprocess.call(['./unblock.sh', ip, iface]);

