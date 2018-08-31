#!/usr/bin/python27

# Copyright scVnner

import os, os.path, socket, sys, time, struct, subprocess, optparse, re, logging, random
from packet import ETH, IP, TCP, eth_size
from ip_man import IP_MAN, FLUSHER
from banner import bann
from utils import url_mode, ssh_mode, alert;


# Colors 
c = {
     'rj': '\033[31;5m', 'vd': '\033[32;5m',
     'am': '\033[33;5m', 'sin': '\033[34;5m',
     'rz': '\033[35;5m', 'cy': '\033[36;5m',
     'bl': '\033[37;5m', 'NULL': '\033[39;5m'
    }

# Messages formats 
MSGS = {
        'url-msg': {
                    'c': c['am']+'[%s]'+c['bl']+':%d visited [ '+c['am']+'%s'+c['bl']+':%d (%s %s) ]',
                    'no-c': '[%s]:%d visited [ %s:%d (%s %s) ]'
                    },
        'ssh-msg': {
                    'c': c['am']+'[%s]'+c['bl']+':%d tried '+c['rj']+'ssh'+c['bl']+' connection [ %d ]',
                    'no-c': '[%s]:%d tried ssh connection [ %d ]'
                    }
        }

    
def read_urls(file):
    lines = None;
    if not os.path.exists(file):
        raise IOError(c.rj+'[ERROR] '+'Could not find |'+file+'|');
    else:
        with open(file, 'r') as fp:
            lines = fp.readlines();
        fp.close();
    return lines;


# This function is used to get only the initial GET request
# and parse it 
def parse_req(data):
    result = '';
    req = {};
    d_ata = data.split('\x0d\x0a');     # \r\n
    req_header = d_ata[0x00].split('\x20');
    for sec in req_header:
        for char in sec:
            if ord(char) > 128 or ord(char) < 30:
                continue;
            else:
                result += char;
        result += '\x20';

    if 'GET' in result:
        req_info = result.split(' ');
        if len(req_info) >= 0x03:
            req['type'] = req_info[0x00];
            req['url'] = req_info[0x01];
            req['proto'] = req_info[0x02];
            return req;


def Mode(opts):
    mode = {};
    if url_mode(opts) and ssh_mode(opts):
        raise ValueError(c['rj']+'[ERROR] Cant choose both url and ssh!');
        sys.exit();

    if not url_mode(opts) and not ssh_mode(opts):
        raise ValueError(c['rj']+'[ERROR] Choose a mode!');
        sys.exit(); 

    elif url_mode(opts) and not ssh_mode(opts):
        if opts.port == 0x00:
            port = 80;
        else:
            port = opts.port;
        mode['type'] = 'url';
        mode['port'] = port;

    elif not url_mode(opts) and ssh_mode(opts):
        if opts.port == 0x00:
            port = 22;
        else:
            port = opts.port;
        mode['type'] = 'ssh';
        mode['port'] = port;

    return mode;


def log(file, msg, stdout=False):
    logger = logging.getLogger(__name__); 
    logger.setLevel(logging.INFO);

    f_form = logging.Formatter('[%(levelname)s] * [%(asctime)s] - %(message)s');
    c_form = logging.Formatter(c['rj']+'[%(levelname)s]'+c['bl']+' * '+c['sin']+'[%(asctime)s]'+c['bl']+' - %(message)s');
    
    if stdout == False:
        logger.handlers = [];
        f_hndl = logging.FileHandler(file);
        f_hndl.setFormatter(f_form);
        f_hndl.setLevel(logging.INFO);
        logger.addHandler(f_hndl);
    else:
        logger.handlers = [];
        s_hndl = logging.StreamHandler(sys.stdout);
        s_hndl.setFormatter(c_form);
        s_hndl.setLevel(logging.INFO);
        logger.addHandler(s_hndl);

    logger.info(msg);


def set_options():
    parser = optparse.OptionParser();

    parser.add_option('-u', '--url', help='Specific url connection monitoring.', action='store', dest='url');
    parser.add_option('-p', '--port', help='Specify the port for your webserver.', action='store', dest='port', default=0);
    parser.add_option('--ssh', help='SSH connection monitoring. [ Works by checking the /var/log/auth.log file ]', action='store', dest='ssh', default=False);
    
    parser.add_option('--ip', help='This option is used in combo with [ --url ].  Specifies your IP.', action='store', dest='ip');
    parser.add_option('-i', '--iface', help='Bind your interface', action='store', dest='iface');
    parser.add_option('--urls', help='Choose your urls file. This file must contain the urls of your website (one on each line) to be matched in the REQUEST', action='store', dest='urls');

    parser.add_option('-b', '--block', help='This option is used in combo with [ --url ]. Choose whether to block connection to hosts if they try to flood [ http ].', action='store_true', dest='block_mode', default=False);

    parser.add_option('--log-lines', help='Number of lines to wait the log file [ all.dat ] to reach before emptying it.', action='store', type='int', dest='log_lines', default=0);
    parser.add_option('-l', '--line-num', help='Specify the last line num of [ all.dat ] to continue numbering from there.', action='store', type='int', dest='line_num', default=0);
    parser.add_option('--limit', help='Number of requests per sec. If any ip exceeds the specified number of requests per sec, gets banned.', action='store', type='int', dest='limit', default=5);
    
    (opts, args) = parser.parse_args();
    return (opts, args)[0x00] ;


def Main():
    opts = set_options();
    mode = Mode(opts);

    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x003)); 
    if opts.iface == None:
        raise ValueError(c.rj+'[ERROR] You must choose your interface!');
        sys.exit();
    else:
        sock.bind((opts.iface, socket.SOCK_RAW));

    if opts.ip == None:
        raise ValueError(c.rj+'[ERROR] You must type in your ip [ex. 192.168.0.101]!');
        sys.exit();

    if opts.urls != None:
        urls = read_urls(opts.urls);
        if opts.line_num != 0:
            counter = int(opts.line_num);
        else:
            counter = 0;
        
        if opts.block_mode == True:
            ip_manager = IP_MAN(opts.iface, opts.limit);
            ip_manager.start();

        if opts.log_lines != 0:
            flusher = FLUSHER(opts.log_lines);
            flusher.start();
    else:
        urls = '';

    while True:
        data = sock.recvfrom(65565);
        packet = data[0x00];
        
        eth = ETH(packet[0x00:eth_size]).parse();
        ip = IP(packet[eth_size:eth_size+20]).parse(); 
        tcp = TCP(packet[(eth_size+ip['tot_len']):(eth_size+ip['tot_len'])+20]).parse();

        data_start = eth_size+ip['tot_len']+tcp['tot_len'];
        recv_data = packet[data_start:];

        if tcp['dest-port'] == mode['port'] and ip['dest-ip'] == opts.ip:
            if mode['type'] == 'url':
                req_header = parse_req(recv_data);
                if req_header is not None and req_header != '':

                    msg = (ip['src-ip'], tcp['src-port'], req_header['url'], tcp['dest-port'], req_header['type'], req_header['proto']);
                    if req_header['url'] == opts.url:
                        log( '', (MSGS['url-msg']['c'] % msg), True );
                        #No colors
                        log('inf.dat', (MSGS['url-msg']['no-c'] % msg), False);
                        alert();

            if urls != '':
                req_header = parse_req(recv_data);
                if req_header is not None and req_header != '':

                    msg = (ip['src-ip'], tcp['src-port'], req_header['url'], tcp['dest-port'], req_header['type'], req_header['proto']);
                    for url in urls:
                        if '[REGEX]' in url:
                            regex = url.split('\x0a')[0x00].split(' [REGEX]')[0x00];
                            if re.match(r''+regex+'', req_header['url']):
                                counter += 1;
                                log('all.dat', (MSGS['url-msg']['no-c'] % msg)+'['+str(counter)+']', False);

                        elif url.split('\x0a')[0x00] == req_header['url']:
                            counter += 1;
                            log('all.dat', (MSGS['url-msg']['no-c'] % msg)+'['+str(counter)+']', False);
                            
            # SSH ...

if __name__ == '__main__':
    print bann;
    Main();
