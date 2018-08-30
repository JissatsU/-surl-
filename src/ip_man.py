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

    def __init__(self, iface, n_req):
        multiprocessing.Process.__init__(self)
        self.HOSTS = {};                         # a dictonary that holds the ips and their access time intervals 
        self.READ_INT = 1;                       # time to wait before next log read 
        self.BLOCKED_FILE = 'blocked.dat';       # a file that stores blocked ips 
        self.IFACE = iface;                      # the interface specified in the [ --iface ] option
        self.N_REQ = n_req;
    

    def run(self):
        while 1:
            time.sleep(self.READ_INT);
            self.store_hosts('all.dat');
            self.check_hosts_time(self.HOSTS);
            self.HOSTS = {};


    # Store each host with its access time intervals in [self.HOSTS]
    def store_hosts(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r+') as fp:
                contents = fp.readlines();
            contents.reverse();

            for line in contents:
                ip = ((line.split('\n')[0].split(' - ')[1]).split(']:')[0])[1:];
                t_time = ((((line.split('\n')[0].split(' - ')[0]).split(' [')[1]).split(' ')[1])[:-1]);

                if ip in self.HOSTS:
                    self.HOSTS[ip].append(t_time);
                else:
                    self.HOSTS[ip] = [];
                    self.HOSTS[ip].append(t_time);


    # Check each host's last [ --limit ] access time intervals 
    # and if the time difference is <= [ --limit ] [1 sec for each request] block the connection 
    def check_hosts_time(self, hosts):
        for host in hosts:
            if len(hosts[host]) >= self.N_REQ:
                t = hosts[host][:self.N_REQ];
                now = ((datetime.datetime.now()).strftime('%H:%M')).split(':');
                to_sub = [ tt for tt in t if tt.split(':')[0] == now[0] and tt.split(':')[1] == now[1] ];

                if len(to_sub) == self.N_REQ:
                    s1 = to_sub[0].split(':')[-1].split(',')[0];
                    s2 = to_sub[-1].split(':')[-1].split(',')[0];

                    if int(s1) - int(s2) < self.N_REQ:
                        if self.is_blocked(host, self.BLOCKED_FILE):
                            pass;
                        else:
                            subprocess.call(['./block.sh', host, self.IFACE]); 
                            self.store_blocked(host, self.BLOCKED_FILE); 

    
    def is_blocked(self, ip, fp):
        if os.path.exists(fp):
            f = open(fp, 'r+');
            l = f.readlines();
            f.close();
            if ip+'\n' in l:
                return True;


    def store_blocked(self, ip, f):
        if os.path.exists(f):
            m = 'a';
        else:
            m = 'w';
        f = open(f, m);
        f.write(ip+'\n');
        f.close();


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

