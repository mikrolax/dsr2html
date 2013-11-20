#/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import subprocess
import shlex
import shutil
import unittest
import dsr2html

class TestError(Exception):
  pass

test_tpl=os.path.join('test','test.tpl')

def clean_test():
  if os.path.exists(os.path.join('test','htmlReport')):
    shutil.rmtree(os.path.join('test','htmlReport'))
  if os.path.exists(os.path.join('_custom')):
    shutil.rmtree(os.path.join('_custom'))
  if os.path.exists(os.path.join('dsr2html.egg-info')):
    shutil.rmtree(os.path.join('dsr2html.egg-info'))

def clean_build():
  if os.path.exists(os.path.join('build')):
    shutil.rmtree(os.path.join('build'))

clean_test()

class Tests(unittest.TestCase):
  def setUp(self):
    self.cmd=['python dsr2html.py -h',
              'python dsr2html.py -d test', 
              'python dsr2html.py -q test',
              'python dsr2html.py -tpl %s -of _custom test' %test_tpl]
    
  def test_module(self):
      dsr2html.process_path(os.path.join('test')) #instanciate and run

  def test_cli(self):
    for cmd in self.cmd:
      print 'test cmd : %s' %cmd
      err=subprocess.call(shlex.split(cmd))
      if err!=0:
        raise TestError('\n\tcmd: %s\n\terror: %s' %(cmd,err))
      #self.assertEqual(err,0)

  def test_build(self):
    cmd='python setup.py sdist'
    err=subprocess.call(shlex.split(cmd))
    if err!=0:
      raise TestError('\n\tcmd: %s\n\terror: %s' %(cmd,err))
    if sys.platform=='win32':
      cmd='python setup.py sdist py2exe'
      err=subprocess.call(shlex.split(cmd))
      if err!=0:
        raise TestError('\n\tcmd: %s\n\terror: %s' %(cmd,err))

    clean_build()
      
  def tearDown(self):
    pass

def testsuite():    
  return unittest.TestLoader().loadTestsFromTestCase(Tests)

if __name__=="__main__":
  results=unittest.TextTestRunner(verbosity=2).run(testsuite())
  sys.exit(0)
  
