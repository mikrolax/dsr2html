#/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import subprocess
import shlex
import shutil
import unittest
import dsr2html
import datetime
          
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
              'python dsr2html.py -tpl %s -of _doc test' %test_tpl]    
    
  def test_1_module_process_path(self):
    dsr=dsr2html.Dsr()
    dsr.name='test process path function'
    dsr.title='process_path() function'
    dsr.description='Test process_path module function'
    path=os.path.join('test')
    start=datetime.datetime.now()
    dsr2html.process_path(path)
    end=datetime.datetime.now()
    dsr.add_step('proces path : %s'%path,'OK',comment='test passed')
    dsr.duration='%s' %(end-start)
    #dsr.tofile(os.path.join('test','module_process_path.json'))
    dsr.tofile(os.path.join('test','module_process_path.Dsr'))
    
  def test_2_cli(self):
    dsr=dsr2html.Dsr()
    dsr.name='test command line interface'
    dsr.title='command line interface tests'
    dsr.description='Test cli() module function'
    start=datetime.datetime.now()
    for cmd in self.cmd:
      try:
        if sys.version_info <= (2,7):
          subprocess.check_call(shlex.split(cmd),stdout=open('cmd.log','w'),stderr=subprocess.STDOUT)
          out=open('cmd.log','r').read()
        else:
          out=subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT)
        dsr.add_step('execute: %s'%cmd,'OK',comment=out)
      except subprocess.CalledProcessError as e:
        dsr.add_step('execute: %s'%cmd,'KO',comment='test return error %s'%(e.returncode))     
        #raise TestError('\n\tcmd: %s\n\terror: %s' %(cmd,err))
    end=datetime.datetime.now()
    dsr.duration='%s' %(end-start)
    #dsr.tofile(os.path.join('test','cli.json'))
    dsr.tofile(os.path.join('test','cli.Dsr'))

  def test_3_build(self):
    dsr=dsr2html.Dsr()
    dsr.name='test dsr2html build'
    dsr.title='dsr2html build'
    dsr.description='Test build'
    start=datetime.datetime.now()
    cmd='python setup.py sdist'
    try:
      if sys.version_info <= (2,7):
        subprocess.check_call(shlex.split(cmd),stdout=open('cmd.log','w'),stderr=subprocess.STDOUT)
        out=open('cmd.log','r').read()
      else:
        out=subprocess.check_output(shlex.split(cmd))
      dsr.add_step('execute: %s'%cmd,'OK',comment=out)
    except subprocess.CalledProcessError as e:
      dsr.add_step('execute: %s'%cmd,'KO',comment='test return error %s'%(e.returncode))     
      #raise TestError('\n\tcmd: %s\n\terror: %s' %(cmd,err))
    if sys.platform=='win32':
      cmd='python setup.py sdist py2exe'
      try:
        if sys.version_info <= (2,7):
          subprocess.check_call(shlex.split(cmd),stdout=open('cmd.log','w'),stderr=subprocess.STDOUT)
          out=open('cmd.log','r').read()
        else:
          out=subprocess.check_output(shlex.split(cmd))
        dsr.add_step('[windows] build binary execute: %s'%cmd,'OK',comment=out)
      except subprocess.CalledProcessError as e:
        dsr.add_step('[windows] build binary execute: %s'%cmd,'KO',comment='test return error %s'%(e.returncode))     
        #raise TestError('\n\tcmd: %s\n\terror: %s' %(cmd,err))
    end=datetime.datetime.now()
    dsr.duration='%s' %(end-start)
    #dsr.tofile(os.path.join('test','build.json'))
    dsr.tofile(os.path.join('test','build.Dsr'))
    clean_build()

  def test_4_errors(self):
    dsr=dsr2html.Dsr()
    dsr.title='errors style'
    dsr.add_step('action 1\naction 2\n','KO',comment='test KO\nerror something\nbut not this\n error 1')
    dsr.add_step('test 2 error','OK',comment='but error when doing something\nandnot this\n\n')
    dsr.add_step('test 3 error','NA',comment='Not available tests\n but some comment error\n')
    dsr.tofile(os.path.join('test','errors_style.Dsr'))
      
  def tearDown(self):
    subprocess.call(shlex.split('python dsr2html.py -q test'))
    
def testsuite():    
  return unittest.TestLoader().loadTestsFromTestCase(Tests)

if __name__=="__main__":
  if os.path.dirname(__file__)!='':
    old=os.getcwd()
    os.chdir(os.path.dirname(__file__)) 
  results=unittest.TextTestRunner(verbosity=2).run(testsuite())
  if os.path.dirname(__file__)!='':
    os.chdir(old)  
  sys.exit(len(results.errors)+len(results.failures))
  
