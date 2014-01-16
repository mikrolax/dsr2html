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

test_path=os.path.join('test')
test_tpl=os.path.join(test_path,'test.tpl')

def clean_test():
  if os.path.exists(os.path.join(test_path,'htmlReport')):
    shutil.rmtree(os.path.join(test_path,'htmlReport'))
  if os.path.exists(os.path.join('_custom')):
    shutil.rmtree(os.path.join('_custom'))
  if os.path.exists(os.path.join('dsr2html.egg-info')):
    shutil.rmtree(os.path.join('dsr2html.egg-info'))
  #remove old Dsr
  
def clean_build():
  if os.path.exists(os.path.join('build')):
    try:
      shutil.rmtree(os.path.join('build'))
    except:
      pass
      
clean_test()

class Tests(unittest.TestCase):
  def setUp(self):
    self.cmd=['python dsr2html.py -h',
              'python dsr2html.py -d test', 
              'python dsr2html.py -q test',
              'python dsr2html.py -tpl %s -of _test_cli test' %test_tpl]
    #install?
    
  def test_0_class_dsr(self):
    """ test module dsr generation """
    dsr=dsr2html.Dsr()
    dsr.name='test module class Dsr()' 
    dsr.title='dsr.Dsr() class'
    dsr.description='test dsr generation with differents styles and error\n\n \
                     test=dsr2html.Dsr()\n \
                     #fill test.name,test.title and test.description\n \
                     add some step\n \
                     test.add_step(action,\'KO\',comment=\'some comment\' \n' 
    dsr.title='test styles and error'
    dsr.add_step('action 1\naction 2\n','KO',comment='test KO\nerror something\nbut not this\n error 1')
    dsr.add_step('test 2 error','OK',comment='but error when doing something\nandnot this\n\n')
    dsr.add_step('test 3 error','NA',comment='Not available tests\n but some comment error\n')
    dsr.tofile(os.path.join(test_path,'errors_style.Dsr'))

  def test_1_module_func_process_path(self):
    """ test module function process_path """
    dsr=dsr2html.Dsr()
    dsr.name='test module function process_path()'
    dsr.title='dsr.process_path() func'
    dsr.description='Test process_path module function' #read docstring
    start=datetime.datetime.now()
    end=datetime.datetime.now()
    dsr.add_step('proces path : %s'%test_path,'OK',comment='test passed')
    dsr.duration='%s' %(end-start)
    #dsr.tofile(os.path.join('test','module_process_path.json'))
    dsr.tofile(os.path.join('test','module_process_path.Dsr'))
    dsr2html.process_path(test_path)
    
  def test_2_cli(self): 
    #write test.cmd ('python dsr2html.py -tpl %s -of _test_cli test' %test_tpl)
    #python dsr2html test.cmd
    #python dsr2html -of doc/test .  
    dsr=dsr2html.Dsr()
    dsr.name='test command line interface'
    dsr.title='command line interface tests'
    dsr.description='Test command line interface : dsr2html and cmd2dsr'
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
    dsr.tofile(os.path.join(test_path,'cli.Dsr'))
    
  def test_3_build(self): 
    #write build.cmd
    f=open(os.path.join('build.cmd'),'w')
    f.write('python setup.py sdist\n')
    if sys.platform=='win32':
      f.write('python setup.py sdist py2exe\n')
    f.close()
    #write build.Dsr
    cmds=['python dsr2html.py %s' %os.path.join('build.cmd')]
    #write build.html ?
    #cmds.append( '' %() )
    for cmd in cmds: # execute
      try:
        if sys.version_info <= (2,7):
          subprocess.check_call(cmd.split(),stdout=open('cmd.log','w'),stderr=subprocess.STDOUT)
          out=open('cmd.log','r').read()
        else:
          out=subprocess.check_output(cmd.split())
      except subprocess.CalledProcessError as e:
        pass
    clean_build()

  def test_5_doc(self):
    # for pimouss...
    import glob
    import shutil
    doc_path=os.path.join('doc')
    if not os.path.exists(doc_path):
      os.makedirs(doc_path) 
    cmd='python dsr2html.py -q -tpl %s -of %s %s' %(test_tpl,os.path.join(doc_path,'test'),test_path)
    subprocess.call(cmd.split())
    files=glob.glob(os.path.join('_doc','*.html'))
    for filepath in files:
      shutil.copyfile(filepath,os.path.join(doc_path,'test','%s.md' %os.path.splitext(os.path.basename(filepath))[0]))
    #shutil.copytree(filepath,os.path.join(doc_path,'test') )
    shutil.copyfile('README.md',os.path.join(doc_path,'index.md'))
    #cmd='python dsr2html.py -q -tpl %s -of %s test ' %(test_tpl,doc_path)
    #subprocess.call(cmd.split())

  #def test_6_server(self):
  #  test_filepath=os.path.join('test')
  #  dsr2html.serve(test_filepath)  
      
  def tearDown(self):
    #clean_test()
    pass
    
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
  
