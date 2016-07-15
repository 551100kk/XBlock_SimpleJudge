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
from easyprocess import EasyProcess

class SimpleJudgeBlock(XBlock):
    Description = String(help="", default=None, scope=Scope.content)
    pro_input = String(help="", default=None, scope=Scope.content)
    pro_output = String(help="", default=None, scope=Scope.content)
    sample_input = String(help="", default=None, scope=Scope.content)
    sample_output = String(help="", default=None, scope=Scope.content)
    
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

    def student_view(self,context):
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
        self.Description = data.get('Description')
        self.pro_input = data.get('pro_input')
        self.pro_output = data.get('pro_output')
        self.sample_input = data.get('sample_input')
        self.sample_output = data.get('sample_output')
        self.display_name = data.get('display_name')
        return {'result': 'success'}
    
    @XBlock.json_handler
    def submit_code(self,data,suffix=''):
        #saving code
        codetime=time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) 
        try:
            path=os.path.join(os.path.dirname(__file__),"judge")
            path=os.path.join(path,data.get('hash'))
            path=os.path.join(path,self.get_user_id())
            os.system('mkdir -p '+path)
            path=os.path.join(path,codetime+'.cpp')
            with open(path,"w") as f:
                f.write(data.get('code'))
        except:
            return {'result': 'error'}
        return {'result': 'success','time':codetime}
    
    @XBlock.json_handler    
    def compile_code(self,data,suffix=''):
        #compiling code
        path=os.path.join(os.path.dirname(__file__),'judge')
        shfile=os.path.join(path,'compile.sh')
        path=os.path.join(path,data.get('hash'))
        path=os.path.join(path,self.get_user_id())
        logfile=os.path.join(path,data.get('time')+'compile.log')
        cppfile=os.path.join(path,data.get('time')+'.cpp')
        resultfile=os.path.join(path,data.get('time')+'.re')
        exefile=os.path.join(path,data.get('time'))
        if os.path.exists(logfile):
            os.remove(logfile)
        os.system('sh '+shfile+' '+cppfile+' '+exefile+' > '+logfile+' 2>&1')

        if self.submited == 0:
            self.total_submited += 1
        self.submited = 1

        if os.path.exists(exefile):
            return {'result': 'success'}
        with open(logfile, 'r') as f:
            result = str(f.read())
        try:
            path=os.path.join(path,'')
            result=result.replace(str(path),'')
        except:
            pass
        with open(resultfile, 'w') as f:
            f.write('Compilation Error')
        self.ce += 1
        return {'result': 'error','comment':result}

    @XBlock.json_handler    
    def upload_testdata(self, data, suffix=''):
        self.data_in.append(str(data.get('input_data')).encode('utf-8'))
        self.data_out.append(str(data.get('output_data')).encode('utf-8'))
        return {'result': 'success'}

    @XBlock.json_handler 
    def runcode(self, data, suffix=''):
        path = os.path.join(os.path.dirname(__file__), 'judge')
        path = os.path.join(path, data.get('hash'))
        path = os.path.join(path, self.get_user_id())
        exefile = os.path.join(path, data.get('time'))
        logfile = os.path.join(path, 'stderr.log')
        resultfile=os.path.join(path,data.get('time')+'.re')
        shfile = os.path.join(path, 'run.sh')
        ansinfile = os.path.join(path, 'in.txt')
        ansoutfile = os.path.join(path, 'out.txt')
        outfile = os.path.join(path, 'run_out.txt')
        for i in range(len(self.data_in)):
            f=open(ansinfile,'w')
            f.write(str(self.data_in[i]))
            f.close()

            f=open(ansoutfile,'w')
            f.write(str(self.data_out[i]))
            f.close()

            cmd=('"%s < %s > %s"' % (exefile,ansinfile,outfile))
            s = EasyProcess('timeout 5 bash -c '+cmd).call(timeout=2)

            if s.timeout_happened:
                with open(resultfile, 'w') as f:
                    f.write('Time Limit Exceed')
                self.tle += 1
                return {'result': 'tle'}
            if s.return_code:
                with open(resultfile, 'w') as f:
                    f.write('Runtime Error')
                self.re += 1
                return {'result': 're'}

            cmd = ('diff -B %s %s' % (ansoutfile,outfile))
            s = EasyProcess(cmd).call()
            if s.stdout != "":
                with open(resultfile, 'w') as f:
                    f.write('Wrong Answer')
                self.wa += 1
                return {'result': 'wa'}
        with open(resultfile, 'w') as f:
            f.write('Accepted')
        self.ac += 1

        if self.solved == 0:
            self.total_solved += 1
        self.solved = 1

        return {'result':'ac'}

    @XBlock.json_handler 
    def submission(self, data, suffix=''):
        path = os.path.join(os.path.dirname(__file__), 'judge')
        path = os.path.join(path, data.get('hash'))
        path = os.path.join(path, self.get_user_id())
        path = os.path.join(path, '')
        cmd = '"ls %s | grep .cpp"' % path
        date = EasyProcess('bash -c ' + cmd).call().stdout.split('\n')
        date = [x.replace('.cpp','') for x in date]
        if len(date) == 1 and date[0] == "":
            date.pop(0)
        result = []
        code = []
        for x in date:
            cmd = '"cat %s"' % (path + x + '.re')
            result.append(EasyProcess('bash -c ' + cmd).call().stdout)
            cmd = '"cat %s"' % (path + x + '.cpp')
            code.append(EasyProcess('bash -c ' + cmd).call().stdout)
        return {'result': result, 'code': code, 'date': date}

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
        return{'ac': self.ac, 'wa': self.wa, 'ce': self.ce, 'tle': self.tle, 're': self.re, 'totalusers': self.total_submited, 'acusers': self.total_solved}
