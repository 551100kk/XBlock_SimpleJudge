import pkg_resources
import requests

from mako.template import Template

from urlparse import urlparse

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List
from xblock.fragment import Fragment

import os
import time
from easyprocess import EasyProcess

class SimpleJudgeBlock(XBlock):
    Description = String(help="", default=None, scope=Scope.content)
    pro_input = String(help="", default=None, scope=Scope.content)
    pro_output = String(help="", default=None, scope=Scope.content)
    sample_input = String(help="", default=None, scope=Scope.content)
    sample_output = String(help="", default=None, scope=Scope.content)
    
    data_in=List(scope=Scope.content)
    data_out=List(scope=Scope.content)
    
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
        
        #js_str = pkg_resources.resource_string(__name__, "static/js/jquery.min.js")
        #frag.add_javascript(unicode(js_str))
        #js_str = pkg_resources.resource_string(__name__, "static/js/bootstrap.min.js")
        #frag.add_javascript(unicode(js_str))
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
            f=open(path,"w")
            f.write(data.get('code'))
            f.close()
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
        exefile=os.path.join(path,data.get('time'))
        if os.path.exists(logfile):
            os.remove(logfile)
        os.system('sh '+shfile+' '+cppfile+' '+exefile+' > '+logfile+' 2>&1')
        if os.path.exists(exefile):
            return {'result': 'success'}
        f=open(logfile,"r")
        result=str(f.read())
        f.close()
        try:
            path=os.path.join(path,'')
            result=result.replace(str(path),'')
        except:
            pass
        return {'result': 'error','comment':result}

    @XBlock.json_handler    
    def upload_testdata(self,data,suffix=''):
        self.data_in.append(str(data.get('input_data')).encode('utf-8'))
        self.data_out.append(str(data.get('output_data')).encode('utf-8'))
        return {'result': 'success'}

    @XBlock.json_handler 
    def runcode(self,data,suffix=''):
        path=os.path.join(os.path.dirname(__file__),'judge')
        path=os.path.join(path,data.get('hash'))
        path=os.path.join(path,self.get_user_id())
        exefile=os.path.join(path,data.get('time'))
        logfile=os.path.join(path,'stderr.log')
        shfile=os.path.join(path,'run.sh')
        ansinfile=os.path.join(path,'in.txt')
        ansoutfile=os.path.join(path,'out.txt')
        outfile=os.path.join(path,'run_out.txt')
        #for i in range(len(data_in)):
        f=open(ansinfile,'w')
        f.write(str(self.data_in[0]))
        f.close()

        f=open(ansoutfile,'w')
        f.write(str(self.data_out[0]))
        f.close()

        cmd=('"%s < %s > %s"' % (exefile,ansinfile,outfile))
        s = EasyProcess('timeout 5 bash -c '+cmd).call(timeout=2)

        if s.timeout_happened:
            return {'result': 'tle'}
        if s.return_code:
            return {'result': 're'}

        cmd=('diff -B %s %s' % (ansoutfile,outfile))
        s = EasyProcess(cmd).call()
        if s.stdout!="":
            return {'result': 'wa'}
        return {'result':'ac'}

