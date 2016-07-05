import pkg_resources
import requests

from urlparse import urlparse

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment

class SimpleVideoBlock(XBlock):
    href = String(help="URL of the video page at the provider", default=None, scope=Scope.content)
    maxwidth = Integer(help="Maximum width of the video", default=800, scope=Scope.content)
    maxheight = Integer(help="Maximum height of the video", default=600, scope=Scope.content)
    watched_count = Integer(help="The number of times the student watched the video", default=1, scope=Scope.user_state)
    def student_view(self,context):
        #html
        html_str = pkg_resources.resource_string(__name__, "static/html/simplevideo.html")
        embed_code = '<iframe width="%d" height="%d" src="https://www.youtube.com/embed/%s" frameborder="0" allowfullscreen></iframe>' % (self.maxwidth,self.maxheight,self.href[17:])
        frag = Fragment(unicode(html_str).format(self=self, embed_code=embed_code))
        #css
        css_str = pkg_resources.resource_string(__name__, "static/css/simplevideo.css")
        frag.add_css(unicode(css_str))
        #javascript
        js_str = pkg_resources.resource_string(__name__, "static/js/simplevideo.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('SimpleVideoBlock')
        
        return frag
        
    @staticmethod    
    def workbench_scenarios():
        return [
            ("simple video",
            """
            <vertical_demo>
                <simplevideo href="https://youtu.be/FNQxxpM1yOs" maxwidth="800" maxheight="600"/>
                <html_demo><div>Rate the video:</div></html_demo>
                <thumbs />
            </vertical_demo>
            """)
        ]  
    @XBlock.json_handler
    def mark_as_watched(self,data,suffix=''):
        if data.get('watched'):
            self.watched_count += 1
        return {'watched_count': self.watched_count}  