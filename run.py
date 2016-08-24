#!/usr/bin/env python

__author__ = 'hoang281283@gmail.com'

import sys
from core import bastion
from core.logo import logo_content

admin_mode = False
if len(sys.argv) > 2:
    admin_mode = sys.argv[2] == '-admin'

sid = sys.argv[1]

bastion.bootstrap(sid, admin_mode, logo_content)
