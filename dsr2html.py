#/usr/bin/python
# -*- coding: utf-8 -*-

__description__=""" simple .dsr (XML subset adapted to tests report) to .html converter """
__project__ = 'dsr2html'
__version__ = '2.0.beta'
__author__ = 'sebastien stang'
__email__ = 'sebastien.stang@gmail.com'
__date__  = '2012-2013'
__license__ ='MIT'

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

import json #py2.6+ only...

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
    logging.warning('to XML not implemented')
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
        result.text = 'OK'
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
    if os.path.splitext(path)[1] =='.json':  
      json.dump(self.dsrdict,open(path,'w'))
    elif os.path.splitext(path)[1] =='.Dsr':
      self.toXML(path)
    else:
      logging.error('error invalid extension %s' %os.path.splitext(path)[1])
           
    
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
      html += '<dl class="dl-horizontal"> \
                <dt>name</dt> <dd> %s </dd> \
                <dt>title</dt><dd> %s </dd> \
                <dt>description</dt>\n\t<dd>%s</dd> \
              </dl>\n' %(elem.find('name').text,elem.find('title').text,elem.find('description').text)
    html += '</div><table id="testtable" class="table"> \
              <thead><tr> \
                <th>StepNb</th> \
                <th>Action</th>\n\t<th>Result</th>\n\t<th>Comment</th>\n\t \
              </tr></thead>\n\t'
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
      actionContent = elem.find('action').text.split('\n')
      html+='<td> %s </td><td>' %(elem.find('number').text)
      if len(actionContent) > 1:
        html+='<ul>'
      for actionContentLine in actionContent:
        if len(actionContent) > 1:
          html+='<li> %s </li>' %(actionContentLine)
        else:  
          html+='%s' %(actionContentLine)
      if len(actionContent) > 1:
        html+='</ul>'
      html+='</td>'
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
      html+='<td>%s</td></tr>' %(comment)  
    html+='</tbody></table>'
    self.indexTable.append([self.name,title,self.duration,self.globalResult])
    return html

  def get_htmlIndex(self):
    html = '<table id="globaltable" class="table tablesorter">\
            <thead><tr><th>Filename</th><th>Title</th><th>Duration</th><th>Global Result</th></tr></thead>'
    for item in self.indexTable:
      links=os.path.splitext(item[0])[0]+'.html'
      if 'OK' in item[3]:
        html+='<tr class="success">'    
      elif 'KO' in item[3]:
        html+='<tr class="error">'          
      else:
        html+='<tr>'    
      html += '<td>%s</td><td>%s</td><td>%s</td>'%(str(item[0]),str(item[1]),str(item[2]))
      if 'OK' in item[3]:
        html+='<td><span class="badge badge-success">%s</span></td>'  %(item[3])
        self.testResultNbOK += 1
      elif 'KO' in item[3]:
        html+='<td><span class="badge badge-warning"rel="tooltip" title="at least one step failed. See details."> \
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
    table = '<table class="table"><thead><tr><th></th><th>Nb</th><th>OK</th><th>KO</th><th>Other</th></tr></thead> \
                <tr><td>Tests</td> \
                <td>%s</td> \
                <td><span class="label label-success"> %s (%.2f &#37) </span> </td>\
                <td> <span class="label label-important"> %s (%.2f &#37) </span></td> \
                <td> <span class="label"> %s (%.2f &#37) </span> </td></tr> \
                <td>Steps</td> \
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
        self.outdir = os.path.join(os.path.dirname(filepath), 'htmlReport') #TODO : use instance param
      else:
        self.outdir=os.path.join(filepath,'htmlReport')
    else:
      self.outdir=outdir
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
    
    
log_format='%(asctime)s:%(levelname)s - %(message)s' #%(name)s
 
def process_path(path,log_level=logging.INFO):
  logging.basicConfig(format=log_format,level=log_level)
  if os.path.exists(path):
    logging.info('process_path %s' %path)
    converter=Dsr2Html()
    converter.run(path) 
  else:
    logging.error('Invalid path : %s' %path)

def process_json(filepath,log_level=logging.INFO):
  logging.basicConfig(format=log_format,level=log_level)
  if os.path.exists(filepath):
    logging.info('process_json %s' %filepath)
    converter=Dsr2Html()
    converter.run_from_json(filepath)
  else:
    logging.error('Invalid path : %s' %filepath)
    
def cli():
  import argparse
  converter=Dsr2Html()
  parser=argparse.ArgumentParser(version='%s' %__version__ ,
                                   description='%s' %__description__,
                                   epilog=' by %s' %(__author__))
  paser_log=parser.add_mutually_exclusive_group()
  paser_log.add_argument("-d", "--debug",action='store_true',default=False,help="verbose output logging")
  paser_log.add_argument("-q", "--quiet",action='store_true',default=False,help="limit output logging to warning/error")
  parser.add_argument("-tpl", "--template",type=str,default=None,help="template file to use.") 
  parser.add_argument("-title",type=str,default=None,help="html page title")
  parser.add_argument("-of","--output_folder",type=str,default=None,help="output folder path.")                 
  parser.add_argument("inpath",type=str,default='',help="input filepath (folder containing .dsr file)")
  args=parser.parse_args()
  if args.quiet:
    logging.basicConfig(format=log_format,level=logging.WARNING)
  elif args.debug:
    logging.basicConfig(format=log_format,level=logging.DEBUG)
  else:
    logging.basicConfig(format=log_format,level=logging.INFO)  
  if args.title:
    converter.title=args.title
  if args.template:
    if os.path.exists(args.template): 
      converter.template=args.template
    else:
      logging.error('template invalid path : %s' %args.template)
  converter.run(args.inpath,outdir=args.output_folder)

if __name__ == "__main__":
  cli()
