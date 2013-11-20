#/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import glob
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.platform == 'win32':
  try:
    import py2exe
  except:
    pass  
import dsr2html
data=glob.glob(os.path.join('static','*.*'))
#if sys.platform == 'win32':
#else:
setup(
    name='dsr2html',
    version=dsr2html.__version__,
    author=dsr2html.__author__,
    author_email=dsr2html.__email__,
    description=dsr2html.__description__,
    license=dsr2html.__license__,
    py_modules=['dsr2html'],        
    entry_points={'console_scripts': ['dsr2html = dsr2html:cli']},      
    #py2exe specific
    data_files=[('static',data)],
    options = {'py2exe': {'bundle_files': 1}}, #, 'optimize': 2 ,'dist_dir':'bin/'
    zipfile = None,    
    console=[{'script':'dsr2html.py',}] #,
    #'icon_resources': [(0, "static/icon.ico")],
   )
