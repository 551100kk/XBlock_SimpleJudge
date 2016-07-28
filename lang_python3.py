from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List
from xblock.fragment import Fragment
import os
import time
import base64
from easyprocess import EasyProcess

def submit_code(self, data):
    #saving code
    codetime = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) 
    try:
        path = os.path.join(os.path.dirname(__file__), "judge", data.get('hash'), self.get_user_id())
        os.system('mkdir -p ' + path)
        path = os.path.join(path, codetime +'.py')
        with open(path, "w") as f:
            f.write(data.get('code'))
    except:
        return {'result': 'error'}
    return {'result': 'success', 'time': codetime}

def compile_code(self, data):
    return {'result': 'success'}

def runcode(self, data, suffix=''):
    path = os.path.join(os.path.dirname(__file__), 'judge', data.get('hash'), self.get_user_id())
    exefile = os.path.join(path, data.get('time') + '.py')
    resultfile=os.path.join(path,data.get('time') + '.re')
    ansinfile = os.path.join(path, 'in.txt')
    ansoutfile = os.path.join(path, 'out.txt')
    
    outfile = os.path.join(path, 'run_out.txt')
    for i in range(len(self.data_in)):
        with open(ansinfile,'w') as f:
            f.write(str(self.data_in[i]))
        with open(ansoutfile,'w') as f:
            f.write(str(self.data_out[i]))

        cmd=('"( cmdpid=$BASHPID; (sleep 6; kill -9 $cmdpid) & exec  python3 %s  < %s > %s )"' % (exefile, ansinfile, outfile))
        s = EasyProcess('bash -c ' + cmd).call(timeout=5)

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

        cmd = ('diff -bB %s %s' % (ansoutfile,outfile))
        s = EasyProcess(cmd).call()
        with open(os.path.join(path, 'test.txt'), 'w') as f:
            f.write(s.stdout)
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

def submission(self, data, suffix=''):
    path = os.path.join(os.path.dirname(__file__), 'judge', data.get('hash'), self.get_user_id(), '')
    cmd = '"ls %s | grep .py"' % path
    date = EasyProcess('bash -c ' + cmd).call().stdout.split('\n')
    date = [x.replace('.py','') for x in date]
    if len(date) == 1 and date[0] == "":
        date.pop(0)
    result = []
    code = []
    for x in date:
        cmd = '"cat %s"' % (path + x + '.re')
        result.append(EasyProcess('bash -c ' + cmd).call().stdout)
        cmd = '"cat %s"' % (path + x + '.py')
        code.append(EasyProcess('bash -c ' + cmd).call().stdout)
    return {'result': result, 'code': code, 'date': date, 'lang': self.Language}