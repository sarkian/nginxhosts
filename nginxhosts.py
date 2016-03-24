#!/usr/bin/env python
# coding: utf-8


import socket
from os import path
from glob import glob
from argparse import ArgumentParser
from argparse import HelpFormatter
from argparse import FileType
from pynginxconfig import NginxConfig


class NginxServers:

    def __init__(self, conf_files,
                 default_addr="127.0.0.1",
                 excluded_hosts=None,
                 config_dir="/etc/nginx",
                 use_listen=False
                 ):
        self.default_addr = default_addr
        self.excluded_hosts = excluded_hosts if isinstance(excluded_hosts, list) else []
        self.config_dir = config_dir
        self.use_listen = use_listen
        self.data = []
        nc = NginxConfig()
        for file in conf_files:
            nc.load(file.read())
            self.process_main(nc)

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "\n".join(map(str, self.data))

    def process_main(self, conf):
        for d in conf:
            if type(d) == dict:
                if d["name"] == "http":
                    self.process_http(d["value"])
                elif d["name"] == "server":
                    self.process_server(d["value"])
            elif type(d) == tuple:
                if d[0] == "include":
                    inc_conf = self.process_include(d[1])
                    self.process_main(inc_conf)

    def process_http(self, conf):
        for d in conf:
            if type(d) == dict:
                if d["name"] == "server":
                    self.process_server(d["value"])
            elif type(d) == tuple:
                if d[0] == "include":
                    inc_conf = self.process_include(d[1])
                    self.process_http(inc_conf)

    def process_server(self, conf):
        server = NginxServer()
        self.process_server_include(conf, server)
        self.data.append(server)

    def process_server_include(self, conf, server):
        for d in conf:
            if type(d) == tuple:
                if d[0] == "listen":
                    server.add_addr(d[1])
                if d[0] == "server_name":
                    server.add_name(d[1])
                if d[0] == "include":
                    self.process_server_include(self.process_include(d[1]), server)

    def process_include(self, globpath):
        if not path.isabs(globpath):
            globpath = path.join(self.config_dir, globpath)
        conf = []
        for fname in sorted(glob(globpath)):
            nc = NginxConfig()
            nc.load(open(fname).read())
            conf += list(nc)
        return conf

    def save_hosts(self):
        names = []
        res = []
        for server in reversed(self.data):
            addr = server.get_addr(self.default_addr) if self.use_listen else self.default_addr
            for name in server.names:
                if name in names or name in self.excluded_hosts or name.find("*") != -1:
                    continue
                names.append(name)
                res.append("%s %s" % (addr, name))
        return "\n".join(reversed(res))

    def save_dnsmasq(self):
        names = []
        res = []
        for server in reversed(self.data):
            addr = server.get_addr(self.default_addr) if self.use_listen else self.default_addr
            s_names = []
            for name in server.names:
                if name in names or name in self.excluded_hosts:
                    continue
                names.append(name)
                s_names.append(name)
            if len(s_names) > 0:
                res.append("address=/%s/%s" % ("/".join(s_names), addr))
        return "\n".join(reversed(res))


class NginxServer:

    def __init__(self, addrs=None, names=None):
        self.addrs = addrs if isinstance(addrs, list) else []
        self.names = names if isinstance(names, list) else []

    def __str__(self):
        return str(self.addrs) + str(self.names)

    def add_addr(self, addr):
        self.addrs.append(addr.strip())

    def add_name(self, name):
        if isinstance(name, str):
            self.names += filter(lambda n: not self.is_addr(n), map(lambda n: n.strip(), name.split(" ")))
        elif isinstance(name, list):
            map(self.add_name, name)

    def get_addr(self, default_addr):
        if len(self.addrs) == 0:
            return default_addr
        for addr in self.addrs:
            addr_parts = addr.split(":")
            if len(addr_parts) > 1 and self.is_addr(addr_parts[0]):
                return addr_parts[0]
        return default_addr

    def is_addr(self, name):
        try:
            socket.inet_aton(name)
            return True
        except socket.error:
            return False


def nginxhosts_main():

    parser = ArgumentParser(formatter_class=lambda prog: HelpFormatter(prog, max_help_position=60, width=130),
                            description="A Nginx configuration parser that exports finded hosts into the hosts or dnsmasq format")
    parser.add_argument("-c", "--config-files", default=None, type=FileType("r"), nargs="+",
                        help="nginx configuration file(s) (default: /etc/nginx/nginx.conf)")
    parser.add_argument("-d", "--config-dir", default="/etc/nginx",
                        help="nginx configuration directory (default: /etc/nginx)")
    parser.add_argument("-a", "--default-addr", default="127.0.0.1",
                        help="default address (default: 127.0.0.1)")
    parser.add_argument("-l", "--use-listen", action="store_true",
                        help="use address from 'listen' directive")
    parser.add_argument("-e", "--excluded-hosts", default="",
                        help="exclude hostnames, comma-separated (default: none)")
    parser.add_argument("-f", "--format", choices=["hosts", "dnsmasq"], default="hosts",
                        help="output format (default: hosts)")
    args = parser.parse_args()

    config_files = args.config_files if isinstance(args.config_files, list) else [open("/etc/nginx/nginx.conf")]
    excluded_hosts = args.excluded_hosts.split(",")
    servers = NginxServers(config_files, args.default_addr, excluded_hosts, args.config_dir, args.use_listen)

    if args.format == "hosts":
        print(servers.save_hosts())
    elif args.format == "dnsmasq":
        print(servers.save_dnsmasq())


if __name__ == "__main__":
    nginxhosts_main()

