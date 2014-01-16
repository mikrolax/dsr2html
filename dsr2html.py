#/usr/bin/python
# -*- coding: utf-8 -*-

__description__=""" simple .dsr (XML subset adapted to tests report) to .html converter """

__project__ = 'dsr2html'
__version__ = '2.0.dev'
__author__  = 'sebastien stang'
__email__   = 'sebastien.stang@gmail.com'
__url__     = 'https://github.com/mikrolax/dsr2html'
__license__ = """Copyright (C) 2012-2014 Sebastien Stang

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import xml.etree.ElementTree  as ET # Overcomes a packaging error in cElementTree, so py2exe works.
import xml.etree.cElementTree as ET
   
from string import Template
import os
import sys
import shutil
import datetime
import logging
import glob   

def _we_are_frozen():
  return hasattr(sys, "frozen")
def _module_path():
  if _we_are_frozen():
    return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
  return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))  
         
static_files=glob.glob(os.path.join(_module_path(), 'static','*.css'))
static_files+=glob.glob(os.path.join(_module_path(), 'static','*.js'))
static_files+=glob.glob(os.path.join(_module_path(), 'static','*.jpg'))
static_files+=glob.glob(os.path.join(_module_path(), 'static','*.png'))

default_title='Test Report'
errors_expressions=['error','ko','failed']

#import json  #py2.6+ only

class Dsr(object):
  def __init__(self):
    self.name='default name'
    self.title='default title'
    self.description='description of the test'
    self.steps=[]
    self.result=None
    self.duration=None
    self.dsrdict_header={'name':self.name,
                         'title':self.title,
                         'description':self.description}
    self.dsrdict_global={'result'    :self.result,
                         'duration'  :self.duration}
    self.dsrdict={'header':self.dsrdict_header,
                  'step'  :self.steps, 
                  'global':self.dsrdict_global}
  
  def add_step(self,action,step_result,comment=''):
    logging.info('%s add step %s' %(self.name,len(self.steps)))
    step={'action':action,
          'step_result':step_result, 
          'comment':comment}
    self.steps.append(step)  

  def get(self):
    return self.dsrdict
      
  def toXML(self,filepath):
    errorFound = 0
    if len(self.steps) > 0:
      test = ET.Element('test')
      header = ET.SubElement(test, 'header')
      name = ET.SubElement(header, 'name')
      name.text = self.name
      title = ET.SubElement(header, 'title')
      title.text = self.title
      description = ET.SubElement(header, 'description')
      description.text = self.description
      steps = ET.SubElement(test, 'steps')
      stepNb = 0
      for item in self.steps:
        step = ET.SubElement(steps, 'step')
        stepNb += 1
        number = ET.SubElement(step, 'number')
        number.text = '%s' %stepNb
        action = ET.SubElement(step, 'action')
        action.text = '%s' %item['action']
        #waited_result = ET.SubElement(step, 'waited_result')
        #waited_result.text = 'Should be equal.'
        comment = ET.SubElement(step, 'comment')
        comment.text = '%s' %item['comment']
        step_result = ET.SubElement(step, 'step_result')
        step_result.text='%s' %item['step_result']
        if step_result.text.lower() in errors_expressions:
          errorFound += 1
      globalid = ET.SubElement(test, 'global')
      result = ET.SubElement(globalid, 'result')
      if errorFound == 0:
        result.text = 'OK (%s)' %stepNb
      else:
        result.text = 'KO (%s/%s)' %(errorFound,stepNb)
      duration = ET.SubElement(globalid, 'duration')
      duration.text = self.duration
      self.tree = ET.ElementTree(test)
      logging.debug('writing %s' %filepath)
      fout=open(filepath, 'w')
      self.tree.write(fout)

  def tofile(self,path):
    logging.info('write %s' %path)
    #if os.path.splitext(path)[1] =='.json':  
    #  json.dump(self.dsrdict,open(path,'w'))
    if os.path.splitext(path)[1] =='.Dsr':
      self.toXML(path)
    else:
      logging.warning('invalid extension %s use .Dsr' %os.path.splitext(path)[1])
      path=path+'.Dsr'
      self.toXML(path)
           

#def make_nav(title,links_left,links_right):
#  html='''<div class="navbar navbar-fixed-top">
#      <div class="navbar-inner">
#        <div class="container">
#          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
#            <span class="icon-bar"></span>
#            <span class="icon-bar"></span>
#            <span class="icon-bar"></span>
#          </a>'''          
#  html=+'''<a class="brand" href="index.html"> %s </a>''' %title
#  html=+'''<div class="nav-collapse">
#            <ul class="nav">'''
#  for name,url in links_left:            
#    html=+'''<li class="divider-vertical"></li>                                     
#             <li><a href="%s"> %s </a></li> ''' %(url,name)
#  html=+'''</ul><ul class="nav pull-right">'''   
#  for name,url in links_right:            
#    html=+'''<li class="divider-vertical"></li>                         
#             <li><a href="%s"> %s </a></li> ''' %(url,name)
#  html=+'''</ul></div></div></div></div>'''      


class Dsr2Html(object):
  def __init__(self): 
    self.tree = ET.ElementTree()
    self.dsrFileLst=[]
    self.indexTable=[]
    self.staticFileLst=[]
    for item in static_files:
      self.staticFileLst.append(item)
    self.duration = ' '
    self.globalResult = ' '
    self.title=default_title
    self.template=os.path.join(_module_path(),'static','layout.tpl')
  
  def init(self): 
    self.perfStartTime = datetime.datetime.now()
    self.processedTestFilesNb = 0
    self.failed = 0
    self.testResultNbOK = 0
    self.testResultNbKO = 0
    self.testResultNbOther = 0
    self.stepResultNb = 0
    self.stepResultNbOK = 0
    self.stepResultNbKO = 0
    self.stepResultNbOther = 0
    self.failedTestLst = []
    self.failedProcessLst = []
    self.dsrFileLst = []
    self.perf=''
    
  def parse(self,fin):          
    """ parse a .Dsr file and return it as a dict. """
    self.tree.parse(fin)
    self.rootElem = self.tree.getroot() 
    self.headerLst = self.rootElem.findall('header')
    self.stepsElem=self.rootElem.find('steps')    
    self.stepElemLst=self.stepsElem.findall('step')      
    for elem in self.rootElem.findall('global'):
      try:
        self.globalResult=elem.find('result').text
      except:
        self.globalResult = 'N/A'
      try:
        self.duration=elem.find('duration').text
      except:
        self.duration = 'N/A'
    self.name=os.path.basename(fin)    
    return dict(headerlst=self.headerLst, steplist=self.stepElemLst)
  
  def get_htmlContentFromTest(self,fin):
    self.parse(fin)       
    html = '<div class="alert alert-info">'
    for elem in self.headerLst:
      title=elem.find('title').text
      #html += '<dl class="dl-horizontal"> \
      #          <dt>name</dt> <dd> %s </dd> \
      #          <dt>title</dt><dd> %s </dd> \
      #          <dt>description</dt>\n\t<dd>%s</dd> \
      #        </dl>\n' %(elem.find('name').text,elem.find('title').text,elem.find('description').text)
      descriptionContent = elem.find('description').text.split('\n')
      description=''
      for line in descriptionContent:
        description+='%s <br>' %(line)
      html += '<dl class="dl-horizontal"> \
                <dt>name</dt> <dd> %s </dd> \
                <dt>title</dt><dd> %s </dd> \
                <dt>description</dt>\n\t<dd>%s</dd> \
              </dl>\n' %(elem.find('name').text,elem.find('title').text,description)
              
    html += '</div><table id="testtable" class="table table-condensed table-hover"> \
              <thead><tr> \
                <th>StepNb</th> \
                <th>Result</th> \
                <th>Action/Comment</th> \
              </tr></thead>'
    for elem in self.stepElemLst:
      comment=''
      commentLst=elem.findall('comment')
      for item in commentLst:
        if item.text:
          comment_lines=item.text.split('\n')
          for line in comment_lines:
            if any(s in line.lower() for s in errors_expressions):
              comment+='<b><span style=\"color:#FF0000\"> %s </span></b><br>' %line
            else:
              comment+=line+'<br>'
      if 'OK' in elem.find('step_result').text:
        html+='<tr class="success">'    
      elif 'KO' in elem.find('step_result').text:
        html+='<tr class="error">'    
      else:
        html+='<tr>'
      html+='<td> %s </td>' %(elem.find('number').text)
      actionContent = elem.find('action').text.split('\n')
      action=''
      if len(actionContent) > 1:
        action+='<ul>'
      for actionContentLine in actionContent:
        if len(actionContent) > 1 and actionContentLine.strip()!='':
          action+='<li> %s </li>' %(actionContentLine)
        else:  
          action+='%s' %(actionContentLine)
      if len(actionContent) > 1:
        action+='</ul>'
      #html+='<td> %s </td>' %action
      #html+='<td>%s</td><td>%s</td>' %(elem.find('number').text,elem.find('action').text)
      step_res=elem.find('step_result').text
      if 'OK' in step_res:
        html+='<td><span class="badge badge-success">%s</span></td>' %(step_res)
        self.stepResultNbOK += 1
      elif 'KO' in step_res:
        html+='<td><span class="badge badge-warning">%s</span></td>' %(step_res)
        self.stepResultNbKO += 1
      else:
        html+='<td><span class="badge">%s</span></td>' %(step_res)  
        self.stepResultNbOther += 1
      self.stepResultNb += 1
      #html+='<td>%s</td></tr>' %(comment)  
      html+='<td>\
              <table><tr><td><strong>Action</strong></td><td> %s </td></tr>\
              <tr><td><strong>Comment</strong></td><td> %s </td></td></table></td></tr>' %(action,comment)
    html+='</tbody></table>'
    self.indexTable.append([self.name,title,self.duration,self.globalResult])
    return html

  def get_htmlIndex(self):
    html = '<table id="globaltable" class="table tablesorter table-condensed table-hover">\
            <thead><tr><th>Filename</th><th>Title</th><th>Duration</th><th>Global Result</th></tr></thead>'
    for item in self.indexTable:
      links=os.path.splitext(item[0])[0]+'.html'
      if 'OK' in item[3]:
        html+='<tr class="success">'    
      elif 'KO' in item[3]:
        html+='<tr class="error">'          
      else:
        html+='<tr>'    
      html += '<td>%s</td><td>%s</td><td>%s</td>'%(str(item[0]),str(item[1]),str(item[2])) # remove button and add links
      if 'OK' in item[3]: 
        html+='<td><span class="badge badge-success">%s</span></td>'  %(item[3])
        self.testResultNbOK += 1
      elif 'KO' in item[3]:
        html+='<td><span class="badge badge-warning"rel="tooltip" title="at least 1 step failed"> \
              %s</span></td>' %(item[3])
        self.testResultNbKO += 1
        self.failedTestLst.append(item[0])
      else:
        html+='<td><span class="badge">%s</span></td>' %(item[3])
        self.testResultNbOther += 1
      html+='<td><a class="btn btn-info" href="%s">View Details</a></td>' %(links) 
      html+='</tr>'      
    html+='</tbody></table>'      
    return html

  def writePage(self,fin,content,outdir):
    logging.debug('write %s' %os.path.join(outdir,os.path.splitext(fin)[0]+'.html'))
    fout=open(os.path.join(outdir,os.path.splitext(fin)[0]+'.html'),'w')
    tpl=open(self.template,'r').read()   
    s = Template(tpl)
    page = s.safe_substitute(content=content.encode('utf-8', 'ignore'),title=self.title,perf=self.perf) 
    fout.write(str(page))

  def copyStaticContent(self,outdir):
    if not os.path.exists(outdir):
      logging.info('create folder %s' %outdir)
      os.makedirs(outdir)
    logging.info('copying static assets to %s' %outdir)
    for item in self.staticFileLst:
      logging.debug('copying %s' %item)      
      shutil.copy(item,outdir)
    
  def getFileLst(self,filepath):
    if os.path.isdir(filepath):
      self.dsrFileLst=glob.glob(os.path.join(filepath,'*.Dsr'))
    else: #one .Dsr only
      if os.path.splitext(filepath)[1]=='.Dsr':
        logging.warning('treat only one .dsr file')
        self.dsrFileLst.append(filepath)
      else:
        logging.error('file extension not supported')

  def writeIndex(self,filepath,content):
    logging.info('writing index.html to %s' %filepath)
    statLst = []
    table = '<table class="table table-condensed"><thead><tr><th></th><th>Nb</th><th>OK</th><th>KO</th><th>Other</th></tr></thead> \
                <tr><td><strong>Tests</strong></td> \
                <td>%s</td> \
                <td><span class="label label-success"> %s (%.2f &#37) </span> </td>\
                <td> <span class="label label-important"> %s (%.2f &#37) </span></td> \
                <td> <span class="label"> %s (%.2f &#37) </span> </td></tr> \
                <td><strong>Steps</strong></td> \
                <td>%s</td> \
                <td><span class="label label-success"> %s (%.2f &#37) </span> </td>\
                <td> <span class="label label-important"> %s (%.2f &#37) </span></td> \
                <td> <span class="label"> %s (%.2f &#37) </span> </td></tr> \
                </tbody></table>' %(self.processedTestFilesNb,
                                    self.testResultNbOK,float(1.0*self.testResultNbOK*100/self.processedTestFilesNb),
                                    self.testResultNbKO,float(1.0*self.testResultNbKO*100/self.processedTestFilesNb),
                                    self.testResultNbOther,float(1.0*self.testResultNbOther*100/self.processedTestFilesNb),
                                    self.stepResultNb,
                                    self.stepResultNbOK,float(1.0*self.stepResultNbOK*100/self.stepResultNb),
                                    self.stepResultNbKO,float(1.0*self.stepResultNbKO*100/self.stepResultNb),
                                    self.stepResultNbOther,float(1.0*self.stepResultNbOther*100/self.stepResultNb))
    stat = ''
    if self.failed > 0:
      stat += '<div class="alert alert-error"><a class="close" data-dismiss="alert" href="#">\xc3\x97</a> \
              <h4 class="alert-heading">Warning!</h4>\n %s .Dsr file parsing failed:' %self.failed
      for item in self.failedProcessLst:
        stat += '<br><a href="%s" rel="tooltip" title="click to view details">%s</a>' %(item,item)
      stat += '</div>'
    stat += '<blockquote><h3>Overview</h3><hr></blockquote> \
               <br><div class="well"> %s </div>' %(table)
    stat += '<blockquote><h3>Details</h3><hr></blockquote>' 
    self.perfEndTime = datetime.datetime.now()
    duration = self.perfEndTime - self.perfStartTime
    self.perf = 'generated on %s/%s/%s processing %s files in %s s' %(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year,self.processedTestFilesNb,duration.seconds) #duration.microseconds
    content=stat+content
    self.writePage('index.html',content,filepath)    
  
  def run(self,filepath,outdir=None):
    logging.info('run %s' %filepath)
    self.init()
    if outdir==None:
      if os.path.isfile(filepath):
        self.outdir = os.path.join(os.path.dirname(filepath), 'htmlReport') #TODO : use param
      else:
        self.outdir=os.path.join(filepath,'htmlReport')
    else:
      self.outdir=outdir
    #clean...
    for item in glob.glob(os.path.join(self.outdir,'*.html')):
      try:
        os.remove(item)
      except:
        logging.warning('failed to remove %s' %item)
    self.indexTable=[] #init!!    
    if os.path.isfile(filepath):
        self.dsrFileLst.append(filepath)
    else:
      self.getFileLst(filepath)
    if not os.path.exists(self.outdir): 
      logging.info('create %s ' %self.outdir)
      os.makedirs(self.outdir)     
    logging.info('processing %s files' %len(self.dsrFileLst))
    if len(self.dsrFileLst) > 0:
      for item in self.dsrFileLst:
        content = self.get_htmlContentFromTest(item)
        self.writePage(os.path.basename(item),content,self.outdir)
        self.processedTestFilesNb += 1
      indexContent=self.get_htmlIndex() 
      content = indexContent.encode()
      self.writeIndex(self.outdir, content)
      if not os.path.exists(os.path.join(self.outdir,'static')):
        os.makedirs(os.path.join(self.outdir,'static'))
      self.copyStaticContent(os.path.join(self.outdir,'static'))
    else:
      logging.warning('Nothing to do, no .Dsr files found')

'''
  def load_json(self,folder): 
    files=glob.glob(os.path.join(folder,'*.json')) #load recursively?
    results={}
    for f in files:
      key='%s' %os.path.basename(f)
      results[key]=json.load(f)
    return results

  def run_from_json(self,filepath):
    logging.warning('not implemented')
    dsr=self.load_json(filepath)
    #output tests/steps table per json file
    pass

def process_json(filepath,log_level=logging.INFO):
  logging.basicConfig(format=log_format,level=log_level)
  if os.path.exists(filepath):
    logging.info('process_json %s' %filepath)
    converter=Dsr2Html()
    converter.run_from_json(filepath)
  else:
    logging.error('Invalid path : %s' %filepath)
'''
    
    
log_format='%(asctime)s|%(levelname)s|%(message)s' #%(name)s
 
def process_path(path,log_level=logging.INFO):
  """ Basic function to convert DSR to HML """
  logging.basicConfig(format=log_format,level=log_level)
  if os.path.exists(path):
    logging.info('process_path %s' %path)
    converter=Dsr2Html()
    converter.run(path) 
  else:
    logging.error('Invalid path : %s' %path)
    
    
class PathChecker(object):
  def __init__(self,path):
    self.path=path
    self.files=[] 
    self.files=self._get_modif() # init list
  
  def _get_modif(self):
    #lst=[]
    #for f in glob.glob(os.path.join(self.path,'*.Dsr')):
    #  lst.append( (f,os.path.getmtime(f)) )  
    #return lst
    return  [ (f,os.path.getmtime(f)) for f in glob.glob(os.path.join(self.path,'*.Dsr')) ]
    
  def check(self):
    files=self._get_modif()
    if files!=self.files:
      self.files=files
      return True
    else:
      return False

import time

log_format='%(asctime)s|%(levelname)s|%(message)s' #%(name)s
def setLog(level=None):
  print 'setLog %s' %level
  if level==None:
    logging.basicConfig(format=log_format,level=logging.INFO)
  elif level=='debug':
    logging.basicConfig(format=log_format,level=logging.DEBUG)
  elif level=='quiet':
    logging.basicConfig(format=log_format,level=logging.WARNING)   
  else:
    logging.basicConfig(format=log_format,level=logging.INFO)

    
def _cli_dsr2html():
  """ dsr2html command line interface """
  import argparse
  converter=Dsr2Html()
  parser=argparse.ArgumentParser(version='%s' %__version__ ,
                                 description='%s' %__description__,
                                 epilog=' by %s' %(__author__))
  paser_log=parser.add_mutually_exclusive_group()
  paser_log.add_argument("-d", "--debug",action='store_true',default=False,help="verbose output logging")
  paser_log.add_argument("-q", "--quiet",action='store_true',default=False,help="limit output logging")
  #paser_serve=subparser
  parser.add_argument("-tpl", "--template",type=str,default=None,help="template file to use.") 
  parser.add_argument("-title",type=str,default=None,help="html page title")
  parser.add_argument("-of","--output_folder",type=str,default=None,help="output folder path.")                 
  parser.add_argument("inpath",type=str,default='',help="input filepath (folder containing .dsr file)")
  args=parser.parse_args()
  if args.quiet:
    setLog('quiet')
  elif args.debug:
    setLog('debug')
  else:
    setLog()
  logging.info('dsr2html: %s' %args.inpath)
  if args.title:
    converter.title=args.title
  if args.template:
    if os.path.exists(args.template): 
      converter.template=args.template
    else:
      logging.error('dsr2html: template invalid path %s' %args.template)
  converter.run(args.inpath,outdir=args.output_folder)

def _cli_cmd2dsr():
  """ cmd2dsr command line interface """
  import argparse
  import subprocess
  parser=argparse.ArgumentParser(version='%s' %__version__ ,
                                 description='Produce Dsr file from a list of command to execute contained in a file.',
                                 epilog=' by %s' %(__author__))
  parser_log=parser.add_mutually_exclusive_group()
  parser_log.add_argument("-d", "--debug",action='store_true',default=False,help="verbose output logging")
  parser_log.add_argument("-q", "--quiet",action='store_true',default=False,help="limit output logging")
  parser.add_argument("-stop","--stop_on_error",action='store_true',default=False,help="Stop after one command failure (return code !=0)")                 
  parser.add_argument("inpath",type=str,default='',help="input filepath (containing 1 command to execute per line)")
  args=parser.parse_args()
  if args.quiet:
    setLog('quiet')
  elif args.debug:
    setLog('debug')
  else:
    setLog()
  if not os.path.exists(args.inpath):
    logging.error('input path does not exist: %s' %args.inpath)
    return 1
  if not os.path.isfile(args.inpath):  
    logging.error('input path is not a file: %s' %args.inpath)
    return 1
  logging.info('cmd2dsr: %s' %args.inpath)
  #cmd2dsr(args.inpath,)
  dsr=Dsr()
  dsr.name='cmd2dsr: %s' %args.inpath
  dsr.title='Execute command from %s' %args.inpath
  cmd_list=open(args.inpath,'r').readlines()
  dsr.description='Execute list of command from %s and get result/output.\n\nCommands:\n\n %s' %(args.inpath,('').join(cmd_list))
  start=datetime.datetime.now()
  for cmd in cmd_list:
    if cmd.rstrip()!='':
      logging.info('cmd2dsr: execute: %s' %cmd.rstrip())
      try:
        if sys.version_info <= (2,7):
          subprocess.check_call(cmd.split(),stdout=open('cmd.log','w'),stderr=subprocess.STDOUT)
          out=open('cmd.log','r').read()
          os.remove('cmd.log')
        else:
          out=subprocess.check_output(cmd.split(),stderr=subprocess.STDOUT)
        dsr.add_step('execute: %s'%cmd,'OK',comment=out)
      except subprocess.CalledProcessError as e:
        dsr.add_step('execute: %s'%cmd,'KO',comment='test return error %s\n%s'%(e.returncode,e.output))
        logging.error('cmd2dsr:error %s for cmd: %s' %(e.returncode,cmd))
        if args.stop_on_error:
          logging.info('cmd2dsr: stop_on_error ON -> Exit!')
          break     
  end=datetime.datetime.now()
  dsr.duration='%s' %(end-start)
  logging.info('cmd2dsr: write %s' %(os.path.join(os.path.dirname(args.inpath),os.path.splitext(os.path.basename(args.inpath))[0]+'.Dsr')))
  dsr.tofile(os.path.join(os.path.dirname(args.inpath),os.path.splitext(os.path.basename(args.inpath))[0]+'.Dsr'))

'''

#def static_server(path,port):#host
#  import SimpleHTTPServer
#  import SocketServer
#  os.chdir(path)
#  Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
#  SocketServer.TCPServer.allow_reuse_address = True
#  httpd = SocketServer.TCPServer(("", port), Handler) # Port 0 means to select an arbitrary unused port
#  print '  Serving: http://localhost:%s' %(port)
#  print '  type Ctrl+C to stop.'
#  httpd.serve_forever()   
#def serve(path,port=None):
#  import threading
#  print '  version: %s' %__version__
#  if port==None:
#    port=0  # Port 0 means to select an arbitrary unused port
#  service   =threading.Thread(name='webserver', target=static_server,args=(os.path.join(path,'htmlReport'),port))
#  converter =threading.Thread(name='dsr2html', target=worker,args=(path,)) # use pool and path list
#  converter.daemon=True
#  service.daemon=True
#  converter.start()
#  try:
#    service.start()
#    while True: 
#      time.sleep(100)
#  except (KeyboardInterrupt,SystemExit):
#    pass
#  print 'Exiting...'

def _cli_serve(): #use cfg file and mikroapp!
  import argparse
  parser=argparse.ArgumentParser(version='%s' %__version__ ,
                                 description='Very basic HTML server with a dsr2html worker.',
                                 epilog=' by %s' %(__author__))
  parser_log=parser.add_mutually_exclusive_group()
  parser_log.add_argument("-d", "--debug",action='store_true',default=False,help="verbose output logging")
  parser_log.add_argument("-q", "--quiet",action='store_true',default=False,help="limit output logging")
  parser.add_argument("-h","--host",type=str,default='localhost',help="specify host to listen (default to localhost)")
  parser.add_argument("-p","--port",type=int,default=8080,help="specify port to listen (default to 8080)")
  parser.add_argument("inpath",type=str,default='',help="input filepath (containing Dsr files)")
  args=parser.parse_args()
  if args.quiet:
    logging.basicConfig(format=log_format,level=logging.WARNING)  # use thread name in format!
  elif args.debug:
    logging.basicConfig(format=log_format,level=logging.DEBUG)
  else:
    logging.basicConfig(format=log_format,level=logging.INFO)  
  if not os.path.exists(args.inpath):
    logging.error('path does not exist: %s' %args.inpath)
    return -1
  serve(args.inpath,args.port) #add host
'''

def worker(path,template=None):
  #print 'checking %s' %path
  working_path=PathChecker(os.path.abspath(path))
  converter=Dsr2Html()
  if template!=None:
    converter.template=template
  #do it once started...
  try:
    converter.run(working_path.path)
  except Exception,e:
    logging.error('%s' %e)
  while True:
    if working_path.check():
      #process_path(working_path.path) 
      try:
        converter.run(working_path.path) 
      except Exception,e:
        logging.error('%s' %e)
    time.sleep(5)

def serve(configfilepath):
  import threading
  import ConfigParser
  if os.path.exists(configfilepath):
    cfg=ConfigParser.SafeConfigParser()
    cfg.read(configfilepath)
    if cfg.has_section('dsr2html'):
      if cfg.has_option('dsr2html','template'):
        template=cfg.get('dsr2html','template')
      else:
        template=None
      if cfg.has_option('dsr2html','log'):
        loglevel=cfg.get('dsr2html','log')
      else:
        loglevel=''
      setLog(loglevel)  
    if cfg.has_section('dsr2html_path'):
      dsr_path_tuple_list=cfg.items('dsr2html_path')
    else:
      dsr_path_tuple_list=[]
    for _name,path in dsr_path_tuple_list:
      converter =threading.Thread(name='dsr2html.%s' %_name, target=worker,args=(path,template))
      converter.daemon=True
      converter.start()
    import mikroapp
    print mikroapp.server
    mikroapp.server(configfilepath)
    
def _cli_serve():
  import argparse
  parser=argparse.ArgumentParser(version='%s' %__version__ ,
                                 description='check for Dsr modification, re-build if needed and serve outputed html',
                                 epilog=' by %s' %(__author__))
  parser_log=parser.add_mutually_exclusive_group()
  parser_log.add_argument("-d", "--debug",action='store_true',default=False,help="verbose output logging")
  parser_log.add_argument("-q", "--quiet",action='store_true',default=False,help="limit output logging")
  parser.add_argument("configfile_path",type=str,default='',help="config file path")
  args=parser.parse_args()
  if args.quiet:
    setLog('quiet')
  elif args.debug:
    setLog('debug')
  else:
    setLog()
  print 'using %s v%s' %(__project__,__version__)  
  serve(args.configfile_path)


if __name__ == "__main__": 
  if os.path.isfile(sys.argv[-1]) and os.path.splitext(sys.argv[-1])[-1]=='.cfg':
    _cli_serve()  
  else:  
    if os.path.isfile(sys.argv[-1]) and os.path.splitext(sys.argv[-1])[-1]!='.Dsr':
      _cli_cmd2dsr()
      sys.argv[-1]=os.path.dirname(os.path.abspath(sys.argv[-1]))  
    _cli_dsr2html()
    
