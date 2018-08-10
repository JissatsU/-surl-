#!/usr/bin/python27

# Copyright scVnner

import os, os.path
import socket
import sys
import time 
import struct
import subprocess
import threading
import optparse
import logging


MSGS = {
        'url-msg': '%s:%d visited [ %s:%d (%s %s) ]',
        'ssh-msg': '%s:%d tried ssh connection [ %d ]'
        }

eth_size = 14;

class c:
	rj = '\033[31;1m';
	vd = '\033[32;1m';
	am = '\033[33;1m';
	sin = '\033[34;1m';
	rz = '\033[35;1m';
	cy = '\033[36;1m';
	bl = '\033[37;1m';
	NULL = '\033[39;1m';

class ETH:
    def __init__(self, body):
        self.body = body;

    def parse(self):
        header = {};
        self.struct = struct.unpack('>6s6sH', self.body);
        self._d_mac = [hex(ord(i)).split('x')[1] for i in self.struct[0]];
        self._s_mac = [hex(ord(i)).split('x')[1] for i in self.struct[1]];
        self._eth_type = hex(self.struct[2]);

        header['dest-mac'] = (':').join(self._d_mac);
        header['src-mac'] = (':').join(self._s_mac);
        header['type'] = self._eth_type;

        return header;

class IP:
    def __init__(self, body):
        self.body = body

    def parse(self):
        header = {};
        self.struct = struct.unpack('>BBHHHBBH4s4s', self.body); 
        self._ip_ver = self.struct[0] >> 4;
        self._ihl = self.struct[0] & 0x00F;
        self._t0s = self.struct[1];
        self._t_len = self._ihl * 4;
        self._ttl = self.struct[5];
        self._proto = self.struct[6];
        self._s_ip = socket.inet_ntoa(self.struct[8]);
        self._d_ip = socket.inet_ntoa(self.struct[9]);

        header['version'] = self._ip_ver;
        header['length'] = self._ihl;
        header['tos'] = self._t0s;
        header['tot_len'] = self._t_len;
        header['ttl'] = self._ttl;
        header['proto'] = self._proto;
        header['src-ip'] = self._s_ip;
        header['dest-ip'] = self._d_ip;

        return header;

class TCP:
    def __init__(self, body):
        self.body = body
    
    def parse(self):
        header = {};
        self.struct = struct.unpack('>HHLLBBHHH', self.body);
        self._s_port = self.struct[0];
        self._d_port = self.struct[1];
        self._seq_num = self.struct[2];
        self._ack_num = self.struct[3];
        self._d0ff = self.struct[4] >> 4;

        header['src-port'] = self._s_port;
        header['dest-port'] = self._d_port;
        header['seq-num'] = self._seq_num;
        header['ack-num'] = self._ack_num;
        header['tot_len'] = self._d0ff * 4;

        return header;

def read_log(file):
    pass;


def parse_req_header(data):
    result = '';
    req = {};
    d_ata = data.split('\r\n');
    req_header = d_ata[0].split(' ');
    for sec in req_header:
        for char in sec:
            if ord(char) > 128 or ord(char) < 30:
                continue;
            else:
                result += char;
        result += ' ';

    if 'GET' in result or 'POST' in result:
        req_info = result.split(' ');
        req['type'] = req_info[0];
        req['url'] = req_info[1];
        req['proto'] = req_info[2];
        return req;


def alert():
    subprocess.call('./beep.sh'); 


def url_mode(opts):
    if opts.url != None:
        return True;

def ssh_mode(opts):
    if opts.ssh != False:
        return True;


def Mode(opts):
    mode = {};
    if url_mode(opts) and not ssh_mode(opts):
        if opts.port == 0:
            port = 80;
        else:
            port = opts.port;
        mode['type'] = 'url';
        mode['port'] = port;

    elif not url_mode(opts) and ssh_mode(opts):
        if opts.port == 0:
            port = 22;
        else:
            port = opts.port;
        mode['type'] = 'ssh';
        mode['port'] = port;
    return mode;


def set_options():
    parser = optparse.OptionParser();
    parser.add_option('-u', '--url', help='Specific url connection monitoring', action='store', dest='url');
    parser.add_option('--ssh', help='SSH connection monitoring', action='store_true', dest='ssh', default=False);
    parser.add_option('-p', '--port', help='This option is used in combo with --SSH | --URL', action='store', dest='port', default=0);
    #parser.add_option('-m', '--method', help='This option is used in combo with -U | --URL.\nSpecifies the http method', action='store', dest='http-method');
    parser.add_option('--ip', help='This option is used in combo with --URL or with --SSH.\n Specifies your IP', action='store', dest='ip');
    parser.add_option('-i', '--iface', help='Bind your interface', action='store', dest='iface');
    
    (opts, args) = parser.parse_args();
    return (opts, args)[0] ;


def Main():
    opts = set_options();
    mode = Mode(opts);

    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003)); 
    if opts.iface == None:
        print '[ERROR] You must choose your interface!'
        sys.exit();
    else:
        sock.bind((opts.iface, socket.SOCK_RAW));

    if opts.ip == None:
        print '[ERROR] You must type in your ip [ex. 192.168.0.101]!'
        sys.exit();

    if url_mode(opts) and ssh_mode(opts):
        print '[ERROR] Choose only one mode!'
        sys.exit();

    elif not url_mode(opts) and not ssh_mode(opts):
        print '[ERROR] Must choose alert mode!'
        sys.exit();
     

    while True:
        data = sock.recvfrom(65565);
        packet = data[0];
        
        eth = ETH(packet[0:eth_size]).parse();
        ip = IP(packet[eth_size:eth_size+20]).parse(); 
        tcp = TCP(packet[(eth_size+ip['tot_len']):(eth_size+ip['tot_len'])+20]).parse();

        data_start = eth_size+ip['tot_len']+tcp['tot_len'];
        recv_data = packet[data_start:];
        
        if mode['type'] == 'url':
            req_header = parse_req_header(recv_data);
            if tcp['dest-port'] == mode['port'] and ip['dest-ip'] == opts.ip:
                if req_header != None:
                    if req_header['url'] == opts.url:
                        print '[WARNING] ' + MSGS['url-msg'] % (ip['src-ip'], tcp['src-port'], req_header['url'], tcp['dest-port'], req_header['type'], req_header['proto']);
                        alert();

        elif mode['type'] == 'ssh':
            pass;

if __name__ == '__main__':
    Main();

