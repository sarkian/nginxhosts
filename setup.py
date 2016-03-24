from distutils.core import setup


setup(
    name="NginxHosts",
    version = "0.1",
    description = "A Nginx configuration parser that exports finded hosts into the hosts or dnsmasq format.",
    author = "Sarkian",
    author_email = "root@dustus.org",
    url = "https://github.com/sarkian/nginxhosts",
    py_modules = ["nginxhosts"],
    install_requires = [
        "argparse>=1.1",
        "pynginxconfig>=0.3.3",
    ],
    entry_points = {
        "console_scripts": [
            "nginxhosts=nginxhosts:nginxhosts_main"
        ]
    }
)
