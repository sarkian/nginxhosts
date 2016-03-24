## NginxHosts

A Nginx configuration parser that exports finded hosts into the hosts or dnsmasq format.

```
usage: nginxhosts.py [-h] [-c CONFIG_FILES [CONFIG_FILES ...]] [-d CONFIG_DIR] [-a DEFAULT_ADDR] [-l] [-e EXCLUDED_HOSTS]
                     [-f {hosts,dnsmasq}]

A Nginx configuration parser that exports finded hosts into the hosts or dnsmasq format

optional arguments:
  -h, --help                                                show this help message and exit
  -c CONFIG_FILES [CONFIG_FILES ...], --config-files CONFIG_FILES [CONFIG_FILES ...]
                                                            nginx configuration file(s) (default: /etc/nginx/nginx.conf)
  -d CONFIG_DIR, --config-dir CONFIG_DIR                    nginx configuration directory (default: /etc/nginx)
  -a DEFAULT_ADDR, --default-addr DEFAULT_ADDR              default address (default: 127.0.0.1)
  -l, --use-listen                                          use address from 'listen' directive
  -e EXCLUDED_HOSTS, --excluded-hosts EXCLUDED_HOSTS        exclude hostnames, comma-separated (default: none)
  -f {hosts,dnsmasq}, --format {hosts,dnsmasq}              output format (default: hosts)
```


Examples

```bash
nginxhosts -e localhost,`hostname` >> /etc/hosts
```

```bash
nginxhosts -f dnsmasq > /etc/NetworkManager/dnsmasq.d/hosts.conf
```

```bash
nginxhosts -c /etc/nginx/sites-enabled/*
```
