from ipykernel.kernelbase import Kernel
from pexpect import TIMEOUT, EOF, spawn
from subprocess import Popen, PIPE
from pathlib import Path
import jupyter_core.paths

import signal
import re
import glob

__version__ = '0.1a1'

class MagmaKernel(Kernel):
    implementation = 'magma_kernel'
    implementation_version = __version__
    
    language_info = {'name': 'magma',
                     'codemirror_mode': 'python',
                     'mimetype': 'text/x-magma',
                     'file_extension': '.m'}

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._prompt="$PEXPECT_PROMPT$"
        self._start_magma()
        self.completions = self._fetch_completions()

    def _fetch_completions(self):
        P=Path(jupyter_core.paths.jupyter_data_dir())
        P=P.joinpath('kernels')
        if not P.exists():
            P.mkdir()
        P=P.joinpath('magma')
        if not P.exists():
            P.mkdir()
        P=P.joinpath('magma-completions.'+self.language_info['version'])
        if P.exists():
            with P.open('r') as F:
                completions = F.read().split()
        else:
            child=Popen("magma",stdin=PIPE,stdout=PIPE)
            child.stdin.write("ListSignatures(Any);".encode())
            child.stdin.close();
            result=child.stdout.read().decode().split()
            completions = sorted({r[:r.index('(')] for r in result if '(' in r})
            with P.open('w') as F:
                F.write('\n'.join(completions))
        return completions
        
    def _start_magma(self):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that magma and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            magma = spawn('magma', echo=False, encoding='utf-8')
            magma.expect_exact('> ')
            banner=magma.before
            magma.sendline('SetLineEditor(false);')
            magma.expect_exact('> ')
            magma.sendline('SetColumns(0);')
            magma.expect_exact('> ')
            magma.sendline('SetPrompt("{}");'.format(self._prompt));
            magma.expect_exact(self._prompt)
            self.child = magma
        finally:
            signal.signal(signal.SIGINT, sig)
        lang_version = re.search("Magma V(\d*.\d*-\d*)",banner).group(1)
        self.banner = "Magma kernel connected to Magma "+lang_version
        self.language_info['version']=lang_version
        self.language_version=lang_version

    def do_help(self, keyword):
        URL="http://magma.maths.usyd.edu.au/magma/handbook/search?chapters=1&examples=1&intrinsics=1&query="+keyword
        content = {
            'source': 'stdout',
            'data': {
#                'text/html':'<iframe src="{}" title="iframe">help</iframe>'.format(URL)
            'text/html':'<a href="{}" target="magma_help">Magma help on {}</a>'.format(URL,keyword)
            }
        }
        self.send_response(self.iopub_socket, 'display_data', content)

#       we could look locally for help, but since these would be "file" URLs
#       we cannot redirect to them anyway.
#        pattern = re.compile('.*(<A  HREF = ".*htm.*".*{}.*</A>)'.format(keyword))
#        results = set()
#        for name in glob.glob('/usr/local/magma/2.23-9/doc/html/ind*.htm'):
#            with open(name,'r') as f:
#                for r in f.readlines():
#                    match=pattern.match(r)
#                    if match:
#                        line = '<A target="magma_help" '+match.group(1)[2:]
#                        results.add(line)
#        content['data']['text/html']="".join(sorted(results))
#        self.send_response(self.iopub_socket, 'display_data', content)        

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
            
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        if code[0] == '?':
            self.do_help(code[1:])
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        interrupted = False
        cmdlines = code.splitlines()
        C=self.child
        try:
            for line in cmdlines:
                C.sendline(line)
                j = 0
                #We use a fairly short timeout intercept and send back
                #updates on what is received on stdout, if there is any.
                counter=10
                timeout=1
                while True:
                    v=C.expect_exact([self._prompt, TIMEOUT],timeout=timeout)
                    if not silent and len(C.before) > j:
                        stream_content = {'name': 'stdout', 'text': C.before[j:]}
                        self.send_response(self.iopub_socket, 'stream', stream_content)
                        j=len(C.before)
                    if v==0:
                        break
                    counter-=1
                    if counter<=0:
                        timeout=min(300,2*counter)
                        counter=10
            output=C.before[j:]
        except KeyboardInterrupt:
            C.sendintr()
            interrupted = True
            C.expect_exact(self._prompt)
            output = C.before[j:]
        except EOF:
            output = C.before[j:] + 'Restarting Magma'
            self._start_magma()

        if not silent:
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}
                
    def do_complete(self, code, cursor_pos):
        cursor_end = cursor_pos
        cursor_start = cursor_end
        while cursor_start>0 and code[cursor_start-1] in "abcdefghijklmnopqrstyuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_":
            cursor_start -= 1
        if cursor_start<cursor_end:
            fragment = code[cursor_start:cursor_end]
            length = len(fragment)
            matches = [C for C in self.completions if fragment == C[:length]]
        else:
            matches = []

        return {'status': 'ok',
            'matches' : matches,
            'cursor_start' : cursor_start,
            'cursor_end' : cursor_end,
            'metadata' : {}}
