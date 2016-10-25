#!/usr/bin/env python
#coding=utf-8

from datetime import datetime
import shutil
import json
import pexpect

g_FileName = 'bigpush.conf'

def exit_with_usage():
    print globals()['__doc__']
    os._exit(1)

def _getCmdInfoFromJson():
    with open(g_FileName, 'r') as f:
        data = json.load(f)
    return data

def getCmdInfo():
    return _getCmdInfoFromJson()


def ssh_login(hostname, password, command):
    try:
        ssh = pexpect.spawn('ssh %s %s' % (hostname, command))
        i = ssh.expect(['[pP]assword:', 'continue connecting (yes/no)?'], timeout=3)
        if i == 0:
            ssh.sendline(password)
            ssh.expect('Authentication successful.')
        elif i == 1:
            ssh.sendline('yes')
            ssh.sendline(password)
    except pexpect.EOF:
        print "pexpect EOF error"
    except pexpect.TIMEOUT:
        print 'connection TIMEOUT'
    except Exception as e:
        pass
    return ssh

def remoteExcute(hostname, password, cmdlist):
    total = len(cmdlist)
    succ = 0
    for i in range(len(cmdlist)):
        fout = open('bigpush_log.txt','ab')

        print '[' + str(i) + '][' + str(len(cmdlist)) + ']'
        print hostname, cmdlist[i]

        text = ''
        text = '[' + datetime.now().isoformat(' ') + ']'
        text += '[' + hostname + ']'
        text += '[' + cmdlist[i]  + ']'

        ssh = ssh_login(hostname, password, cmdlist[i])
        res = ssh.read()
        res.strip()
        ssh.expect(pexpect.EOF)
        ssh.close()
        if ssh.exitstatus == 0:
            print 'excute success!'
            text += '[SUCCESS]'
            succ += 1
        else:
            print 'ERROR!'
            text += '[ERROR]'
        text += res[3:]
        fout.write(text + '\r\n')
        fout.close()
    print '[Total:' + str(total) + '][Success:' + str(succ) + ']'
 
if __name__ == '__main__':
    data = getCmdInfo()
    for i in range(len(data)):
        print 'command list=========', i
        cmdlist = data[str(i)]['Command']
        hostlist = data[str(i)]['Hostlist']
        for host in hostlist:
            remoteExcute(host['Hostname'], host['Password'], cmdlist) 

