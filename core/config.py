__author__ = 'hoang281283@gmail.com'

default_user = 'root'
default_port = 22
default_record = True

hosts = [
    {'user': 'toto', 'domain': '192.168.10.1', 'port': 2222, 'category': 'API, Cache', 'desc': 'Blah blah 1'},
    {'user': 'tutu', 'domain': '192.168.10.2', 'category': 'API, DB, RabbitMQ', 'record': False, 'desc': 'Blah blah 2'},
    {'user': 'toto', 'domain': '192.168.10.3', 'category': 'API, RabbitMQ', 'desc': 'Blah blah 3'},
    {'user': 'toto2', 'domain': '192.168.10.3', 'category': 'Elastic Search', 'desc': 'Blah blah 3'},
    {'user': 'toto2', 'domain': '192.168.10.3', 'category': 'API, Nginx', 'desc': 'Blah blah 3'},
    {'user': 'toto', 'domain': '192.168.10.3', 'category': 'API Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto', 'domain': '192.168.10.3', 'category': 'API Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto2', 'domain': '192.168.10.3', 'category': 'Nginx Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto2', 'domain': '192.168.10.4', 'category': 'API Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto1', 'domain': '192.168.10.7', 'category': 'API Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto1', 'domain': '192.168.10.8', 'port': 211, 'category': 'Tomcat, Jetty', 'desc': 'Blah blah 3'},
    {'user': 'toto1', 'domain': '192.168.10.9', 'category': 'Nginx Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto1', 'domain': '192.168.10.10', 'category': 'Nginx Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto', 'domain': '192.168.10.11', 'category': 'API Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto', 'domain': '192.168.10.12', 'category': 'Tomcat, Jetty', 'desc': 'Blah blah 3'},
    {'user': 'toto', 'domain': '192.168.10.13', 'category': 'DB Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto2', 'domain': '192.168.10.14', 'category': 'DB Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto', 'domain': '192.168.10.15', 'category': 'DB Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto', 'domain': '192.168.10.16', 'category': 'API Servers', 'desc': 'Blah blah 3'},
    {'user': 'toto', 'domain': '192.168.10.17', 'category': 'API Servers', 'desc': 'Blah blah 3'},
    {'user': 'titi', 'domain': '192.168.10.18', 'category': 'Web Servers', 'desc': 'Blah blah 4'}
]

tmux_session_name = "bastion"

