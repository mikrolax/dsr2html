
## What are .dsr file
- - -

.Dsr files are XML file describing tests results. 
Here is a simple minimal example:
	
        <test>

        <header>
          <name> A name </name>
          <title> A title </title>
          <description> some description of the test </description>
        </header>

        <steps>

          <step>
            <number> 1 </number>
            <action> Write something related to this step </action>
            <step_result> OK </step_result>
          </step>
          
        </steps>

        <global>
          <duration> </duration>
          <result> OK </result>
        </global>

        </test>
	
	
A test contains many 'steps'	 


## Install / Use  
- - -  
* install  

dsr2html does not need to be installed, but you can:  
  
        python setup.py install


* use   
If installed:  

        dsr2html -v

If not installed:  

        python /path/to/dsr2html.py -v

If you use windows static binary, use `dsr2html.exe -v`  

## Command line interface  
- - -  

        usage: dsr2html.py [-h] [-v] [-d | -q] [-tpl TEMPLATE] [-title TITLE]
               [-of OUTPUT_FOLDER]
               inpath

        simple .dsr (XML) to .html converter, with some fancy CSS & JS

        positional arguments:
          inpath                input filepath (folder containing .dsr file)

        optional arguments:
          -h, --help            show this help message and exit
          -v, --version         show program's version number and exit
          -d, --debug           verbose output logging
          -q, --quiet           limit output logging to warning/error
          -title TITLE          html page title
          -tpl TEMPLATE, --template TEMPLATE
              template file to use.
          -of OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
              output folder path.


## Credits  
- - -  

See LICENSE file and javascript files contained in static for more infos.  

