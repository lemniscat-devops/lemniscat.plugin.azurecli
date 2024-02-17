# -*- coding: utf-8 -*-
# above is for compatibility of python2.7.11

import logging
import os
import subprocess, sys   
from lemniscat.core.util.helpers import LogUtil
import re

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.setLoggerClass(LogUtil)
log = logging.getLogger(__name__.replace('lemniscat.', ''))

class AzureCli:
    def __init__(self):
        pass
    
    def cmd(self, cmds, **kwargs):
        outputVar = {}
        capture_output = kwargs.pop('capture_output', True)
        is_env_vars_included = kwargs.pop('is_env_vars_included', False)
        if capture_output is True:
            stderr = subprocess.PIPE
            stdout = subprocess.PIPE
        else:
            stderr = sys.stderr
            stdout = sys.stdout
            
        environ_vars = {}
        if is_env_vars_included:
            environ_vars = os.environ.copy()

        p = subprocess.Popen(cmds, stdout=stdout, stderr=stderr,
                             cwd=None, shell=True)
        
        while p.poll() is None:
            lines = p.stdout.readlines()
            errors = p.stderr.readlines()
            for line in lines:
                ltrace = line.decode('utf-8').rstrip('\r\n')
                m = re.match(r"^\[lemniscat\.pushvar\] (?P<key>\w+)=(?P<value>.*)", str(ltrace))
                if(not m is None):
                    outputVar[m.group('key').strip()] = m.group('value').strip()
                else:
                    log.debug(f'  {ltrace}')
            for error in errors:
                ltrace = error.decode("utf-8").rstrip("\r\n")
                if(ltrace.startswith("ERROR:")):
                    log.error(f'  {ltrace}')
                else:
                    log.warning(f'  {ltrace}')
        
        out, err = p.communicate()
        ret_code = p.returncode

        if capture_output is True:
            out = out.decode('utf-8')
            err = err.decode('utf-8')
        else:
            out = None
            err = None

        return ret_code, out, err, outputVar
    
    def append_loginCommand(self, type):
        self.cmd([type, '-Command', "az config unset core.allow_broker"])
        self.cmd([type, '-Command', f"az login --service-principal -u {os.environ['ARM_CLIENT_ID']} -p {os.environ['ARM_CLIENT_SECRET']} --tenant {os.environ['ARM_TENANT_ID']}"])
        self.cmd([type, '-Command', f"az account set --subscription {os.environ['ARM_SUBSCRIPTION_ID']}"])
        
    def run(self, type, command):
        self.append_loginCommand(type)
        return self.cmd([type, '-Command', command])

    def run_script(self, type, script):
        self.append_loginCommand(type)
        return self.cmd([type, "-File", script])

    def run_script_with_args(self, type, script, args):
        self.append_loginCommand(type)
        return self.cmd([type, "-File", script, args])