from database.models import *

import sys

import os

os.system('rm data.db')

setup_all()
create_all()
