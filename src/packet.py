#!/usr/bin/python27

import socket
import struct

eth_size = 0x0E;

class ETH:
    def __init__(self, body):
        self.body = body;

    def parse(self):
        header = {};
        self.struct = struct.unpack('>6s6sH', self.body);
        self._d_mac = [hex(ord(i)).split('x')[0x01] for i in self.struct[0x00]];
        self._s_mac = [hex(ord(i)).split('x')[0x01] for i in self.struct[0x01]];
        self._eth_type = hex(self.struct[0x02]);

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
        self._ip_ver = self.struct[0x00] >> 0x004;
        self._ihl = self.struct[0x00] & 0x00F;
        self._t0s = self.struct[0x01];
        self._t_len = self._ihl * 0x04;
        self._ttl = self.struct[0x05];
        self._proto = self.struct[0x06];
        self._s_ip = socket.inet_ntoa(self.struct[0x08]);
        self._d_ip = socket.inet_ntoa(self.struct[0x09]);

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
        self._s_port = self.struct[0x00];
        self._d_port = self.struct[0x01];
        self._seq_num = self.struct[0x02];
        self._ack_num = self.struct[0x03];
        self._d0ff = self.struct[0x04] >> 0x004;

        header['src-port'] = self._s_port;
        header['dest-port'] = self._d_port;
        header['seq-num'] = self._seq_num;
        header['ack-num'] = self._ack_num;
        header['tot_len'] = self._d0ff * 0x004;

        return header;
