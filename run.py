#!/usr/bin/env python

__author__ = 'hoang281283@gmail.com'

import sys
from core import bastion

sid = sys.argv[1]
bastion.bootstrap(sid)
