import urllib
import urllib2
import cookielib
form_data = {
'utf8':"✓",
'authenticity_token':"ia2kGn363ICS+M3Yt0ItQVmc8+84NMt8Rut7A7RZXnLjHDHwxEkZNZAns59fdIw/+OSSJ+nuU1dZhLcyhUHaVw==",
'gist[description]':"",
'gist[contents][][oid]':"",
'gist[contents][][name]':"123.java",
'new_filename':"123.java",
'content_changed':"true",
'gist[contents][][value]':"""import java.util.Scanner;
public class Main{
	public static void main(String[] args){
		Scanner sc = new Scanner(System.in);
		int a = sc.nextInt();
		int b = sc.nextInt();
for(int i=0;i<1000000000;i++)for(int j=0;j<1000000000;j++){int aa=5; aa=aa/a; b+=aa;}
		System.out.printf("%d\n",a+b+1);
	}
}""",
'gist[public]':"1"
}
cj = cookielib.LWPCookieJar()  
cookie_support = urllib2.HTTPCookieProcessor(cj)  
opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)  
urllib2.install_opener(opener)
url = "https://gist.github.com"
request = urllib2.Request(url) 
request.add_header("User-Agent","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36")
response = urllib2.urlopen(request)

print response.read()
