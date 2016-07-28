import pkg_resources
import requests

from mako.template import Template

from urlparse import urlparse

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List
from xblock.fragment import Fragment

import os
import time
import urllib
import urllib2
import base64
from easyprocess import EasyProcess

import lang_C
import lang_JAVA
import lang_python3

class SimpleJudgeBlock(XBlock):

    #DATABASE

    Language = String(help="", default='JAVA', scope=Scope.content)
    Description = String(help="", default=None, scope=Scope.content)
    pro_input = String(help="", default=None, scope=Scope.content)
    pro_output = String(help="", default=None, scope=Scope.content)
    sample_input = String(help="", default=None, scope=Scope.content)
    sample_output = String(help="", default=None, scope=Scope.content)
    
    data_name=List(scope=Scope.content)
    data_in=List(scope=Scope.content)
    data_out=List(scope=Scope.content)
    
    display_name = String(help="", default="Judge", scope=Scope.content) 

    ac = Integer(help="", default=0, scope=Scope.user_state_summary)
    wa = Integer(help="", default=0, scope=Scope.user_state_summary)
    tle = Integer(help="", default=0, scope=Scope.user_state_summary)
    ce = Integer(help="", default=0, scope=Scope.user_state_summary)
    re = Integer(help="", default=0, scope=Scope.user_state_summary)

    total_submited = Integer(help="", default=0, scope=Scope.user_state_summary)
    total_solved = Integer(help="", default=0, scope=Scope.user_state_summary)

    submited = Integer(help="", default=0, scope=Scope.user_state)
    solved = Integer(help="", default=0, scope=Scope.user_state)

    #student
    def reset(self):
        self.ac = 0
        self.wa = 0
        self.tle = 0
        self.ce = 0
        self.re = 0
        self.total_submited = 0
        self.total_solved = 0
        self.submited = 0
        self.solved = 0

    def student_view(self,context):
        #self.reset()
        #html
        html_str = pkg_resources.resource_string(__name__, "static/html/simplejudge.html")
        frag = Fragment(unicode(html_str).format(self=self))
        #css
        css_str = pkg_resources.resource_string(__name__, "static/css/style.css")
        frag.add_css(unicode(css_str))
        
        css_str = pkg_resources.resource_string(__name__, "static/css/simplejudge.css")
        frag.add_css(unicode(css_str))
        #javascript
        js_str = pkg_resources.resource_string(__name__, "static/js/simplejudge.js")
        frag.add_javascript(unicode(js_str))

        js_str = pkg_resources.resource_string(__name__, "static/js/jquery.flot.js")
        frag.add_javascript(unicode(js_str))
        js_str = pkg_resources.resource_string(__name__, "static/js/jquery.flot.pie.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('main')
        
        return frag
    
    #studio

    def studio_view(self, context):
        #html
        html_str = pkg_resources.resource_string(__name__, "static/html/simplejudge_edit.html")
        html_str=Template(html_str).render(data_in=self.data_in,data_out=self.data_out)
        frag = Fragment(unicode(html_str).format(self=self))
        #javascript
        js_str = pkg_resources.resource_string(__name__, "static/js/simplejudge_edit.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('main')
        return frag
    
    def get_user_id(self):
        return self.xmodule_runtime.anonymous_student_id
    
    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        self.Language = data.get('Language')
        self.Description = data.get('Description')
        self.pro_input = data.get('pro_input')
        self.pro_output = data.get('pro_output')
        self.sample_input = data.get('sample_input')
        self.sample_output = data.get('sample_output')
        self.display_name = data.get('display_name')
        return {'result': 'success'}
    
    @XBlock.json_handler    
    def upload_testdata(self, data, suffix=''):
        path = os.path.join(os.path.dirname(__file__), 'judge')
        zipfile = os.path.join(path, 'tmp.zip')
        desfile = os.path.join(path, 'tmp')
        zipdata = data.get('zipdata')
        zipdata = zipdata.replace('data:application/zip;base64,', '')
        zipdata = base64.b64decode(zipdata)
        with open(zipfile, 'wb') as f:
            f.write(zipdata)
        #extract
        os.system('unzip %s -d %s' % (zipfile, desfile))

        cmd = '"ls %s | grep .in"' % desfile
        input_data = EasyProcess('bash -c ' + cmd).call().stdout.split('\n')
        cmd = '"ls %s | grep .out"' % desfile
        output_data = EasyProcess('bash -c ' + cmd).call().stdout.split('\n')
        
        #check files name
        if len(input_data) != len(output_data):
            os.system('rm %s' % zipfile)
            os.system('rm -r %s' % desfile)
            return {'result': '.in files does not match .out files'}

        for x, y in zip(input_data, output_data):
            if x.replace('.in', '') != y.replace('.out', ''):
                os.system('rm %s' % zipfile)
                os.system('rm -r %s' % desfile)
                return {'result': '.in files does not match .out files'}

        #read in out files
        self.data_name = []
        self.data_in = []
        self.data_out = []

        for x, y in zip(input_data, output_data):
            self.data_name.append(x.replace('.in', ''))
            path = os.path.join(desfile, x)
            cmd = '"cat %s"' % (path)
            self.data_in.append(EasyProcess('bash -c ' + cmd).call().stdout)
            path = os.path.join(desfile, y)
            cmd = '"cat %s"' % (path)
            self.data_out.append(EasyProcess('bash -c ' + cmd).call().stdout)

        os.system('rm %s' % zipfile)
        os.system('rm -r %s' % desfile)
        return {'result': 'success'}

    @XBlock.json_handler    
    def show_testdata(self, data, suffix=''):
        return {'name': self.data_name, 'in': self.data_in, 'out': self.data_out, 'Language': self.Language}


    ############Judge Start############
    lang = {
        'C++': lang_C,
        'JAVA': lang_JAVA,
        'python3': lang_python3,
    }

    @XBlock.json_handler
    def submit_code(self,data,suffix=''):
        return self.lang[self.Language].submit_code(self, data) 
    
    @XBlock.json_handler    
    def compile_code(self,data,suffix=''):
        return self.lang[self.Language].compile_code(self, data)

    @XBlock.json_handler 
    def runcode(self, data, suffix=''):
        return self.lang[self.Language].runcode(self, data)

    @XBlock.json_handler 
    def submission(self, data, suffix=''):
        return self.lang[self.Language].submission(self, data)

    ###################################

    @XBlock.json_handler 
    def codepad(self, data, suffix=''):
        url = "http://codepad.org"
        request = urllib2.Request(url) 
        request.add_header("User-Agent","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36")
        form_data = {
            "lang": "C++", 
            "code": data.get('code'),
            "submit": "Submit",
        }

        form_data = urllib.urlencode(form_data)
        response = urllib2.urlopen(request, data=form_data, timeout=5)  
        url = response.url
        return {'url': url}

    @XBlock.json_handler 
    def statistic(self, data, suffix=''):
        return {'ac': self.ac, 'wa': self.wa, 'ce': self.ce, 'tle': self.tle, 're': self.re, 
                'totalusers': self.total_submited, 'acusers': self.total_solved, 'submited': self.submited, 'solved': self.solved, 'Language': self.Language}
