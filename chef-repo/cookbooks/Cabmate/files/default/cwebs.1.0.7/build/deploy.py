import os
import sys

# ONLY INSTALL ON FRESH BOX!!!
config_fresh_install = True
# VERSION OF THE INSTALL SCRIPT
config_fresh_version = '1.0.6'
# True if include "sudo" in linux command 
config_include_sudo_in_command = True

#Folder where 2.7 is installed
altfolder = "/usr/local/bin"

# CWEBS root folder 
# code will be located in <config_cwebs_root>/cwebs
# default folders 
# /cwebs/cwebs for code
# /cwebs/cwebs.install for install stuff
config_cwebs_root = "/cwebs"

# location of cwebs distribution packages
distr_root = "/home/ec2-user/cwebs.distr"
cwebs_distr = "cwebs.1.0.8.tar.gz"
packs_distr = "cwebs_packages.tar.gz"

# packages - do not touch, added a new package
# for version 1.6
packs = [
#{"pack": "cython", "version": "0.19.2", "instruct": ""}, 
{"pack": "greenlet", "version": "0.4.2", "instruct": ""}, 
{"pack": "gevent", "version": "1.0.1", "instruct": ""},  
{"pack": "bottle", "version": "0.11.6", "instruct": ""}, 
{"pack": "mysql-connector-python", "version": "1.2.2", "instruct": "--allow-external mysql-connector-python"}, 
{"pack": "mysql-connector-python-rf", "version": "1.2.3", "instruct": "--allow-external mysql-connector-python"}, 
{"pack": "MySQL-python", "version": "", "instruct": ""}, 
{"pack": "requests", "version": "", "instruct": ""},
{"pack": "sysv_ipc", "version": "", "instruct": ""}]  


supervisord_conf_contents = '''
; supervisor config file

[unix_http_server]
file=/var/run/supervisor.sock   ; (the path to the socket file)
chmod=0700                       ; sockef file mode (default 0700)

[supervisord]
logfile=/var/log/supervisor/supervisord.log ; (main log file;default $CWD/supervisord.log)
pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
childlogdir=/var/log/supervisor            ; ('AUTO' child log dir, default $TEMP)

; the below section must remain in the config file for RPC
; (supervisorctl/web interface) to work, additional interfaces may be
; added by defining them in separate rpcinterface: sections
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock ; use a unix:// URL  for a unix socket

; The [include] section can just contain the "files" setting.  This
; setting can list multiple files (separated by whitespace or
; newlines).  It can also contain wildcards.  The filenames are
; interpreted as relative to this file.  Included files *cannot*
; include files themselves.

[inet_http_server]
port = localhost:9001

[include]
files = /etc/supervisor/conf.d/*.conf'''

cwebs_conf_contents = '''
[program:cwebs]
command=/cwebs/cwebs_venv/bin/python -u /cwebs/cwebs/app/cwebsserv.py
priority=999
autostart=true
autorestart=true
startsecs=0
startretries=3
exitcodes=0,2
stopwaitsecs=0
stdout_logfile = /var/log/supervisor/cwebs.stdout
stderr_logfile = /var/log/supervisor/cwebs.stderr
stdout_logfile_maxbytes = 10MB
stderr_logfile_maxbytes = 10MB
'''

ss = ""
if config_include_sudo_in_command:
    ss = "sudo " 

def invalid_folder(fld):
    print 'exiting install...'
    print 'folder ' + fld + ' already exists'
    sys.exit()

def get_pip_string(pip, packdic):
    s = pip + " " + packdic["pack"]
    print 's:', s
    if packdic["version"] != "":
        s = s + "==" + packdic["version"]
        print 's:', s
    if packdic["instruct"] != "": 
        s = s + " " + packdic["instruct"]
        print 's:', s 
    print 'returning s:', s    
    return s 
 
if __name__ == '__main__':
    cwd = os.getcwd()
   
    if not config_fresh_install:
        print 'Only fresh installed is implemented'
	sys.exit()
	
    archive_cwebs = os.path.join(distr_root, cwebs_distr) 
    if not os.path.exists(archive_cwebs):
        print 'exiting install...'
        print 'distribution file ' + archive_cwebs + ' does not exist'
        sys.exit()
    
    archive_packs = os.path.join(distr_root, packs_distr) 
    if not os.path.exists(archive_packs):
        print 'exiting install...'
        print 'package file ' + archive_packs + ' does not exist'
        sys.exit()
    
    print 'enter key to install os updates...'
    raw_input()
    os.system(ss + "yum install -y python-setuptools") 
    os.system(ss + "yum install -y python-devel") 
    os.system(ss + "yum install -y libevent-devel") 
    os.system(ss + "yum install -y mysql-devel")
    os.system(ss + "yum -y groupinstall 'Development Tools' ")
    os.system(ss + "yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel")
    os.system(ss + "yum install -y gcc") 
    os.system(ss + os.path.join(altfolder, "easy_install") + " pip")
    #os.system(ss + "/usr/local/bin/pip install virtualenv") 
    os.system(ss + os.path.join(altfolder, "pip") + "install virtualenv")
    
    if os.path.exists(config_cwebs_root):
        invalid_folder(config_cwebs_root)
    config_cwebs_code_fld = os.path.join(config_cwebs_root, "cwebs")
    config_cwebs_install_fld = os.path.join(config_cwebs_root, "cwebs.install")
    for fld in [config_cwebs_code_fld, config_cwebs_install_fld]:
        if os.path.exists(fld):
           invalid_folder(fld)

    print 'Enter key to create folder structure and virtual env...'
    raw_input()
   
  
    os.system(ss + "mkdir " + config_cwebs_root)
    os.system(ss + "mkdir " + config_cwebs_code_fld)
    os.system(ss + "mkdir " + config_cwebs_install_fld) 
    os.chdir(config_cwebs_root)
    print 'current work dir ', os.getcwd()
    print 'config_cwebs_root', config_cwebs_root
    os.system(ss + os.path.join(altfolder, "virtualenv " )  + os.path.join(config_cwebs_root, "cwebs_venv"))
    print 'activating virtual environment '
    print "source " + os.path.join(config_cwebs_root, "cwebs_venv/bin/activate") 
    os.system("source " + os.path.join(config_cwebs_root, "cwebs_venv/bin/activate"))
    for apack in packs:
        cmd = get_pip_string(os.path.join(config_cwebs_root, "cwebs_venv/bin/pip") + " install", apack)
	print 'pwd: ', os.getcwd(), 'logging: ', cmd
        print 'executing ', ss + cmd
        os.system(ss + cmd)
    os.system("deactivate")
    print 'Enter key to to proceed with unpacking distribution...'
    raw_input()
    
    os.system(ss + "mv " + os.path.join(distr_root, cwebs_distr) + " /cwebs/cwebs.install/.") 
    os.system(ss + "mv " + os.path.join(distr_root, packs_distr) + " /cwebs/cwebs.install/.")
    os.chdir("/cwebs/cwebs.install") 
    
    try:
        os.system(ss + "tar -zxvf " + os.path.join("/cwebs/cwebs.install", cwebs_distr))
    except Exception as e:
        print 'can not unpack ', os.path.join("/cwebs/cwebs.install", cwebs_distr)
	sys.exit()	
    

    try:
        #os.system(ss + "xz -d Python-2.7.8.tar.xz")
        os.system(ss + "tar -xvf Python-2.7.8.tar ")
        # Enter the directory:
        os.system(ss + " cd Python-2.7.8")

        # Run the configure:
        os.system(ss + " ./configure --prefix=/usr/local")

        #compile and install it:
        os.system(ss + "make  ")
        os.system(ss + " make altinstall")
    except Exception as e:
        print "can not build python 2.7"
        sys.exit()  

    try:
        os.system(ss + "tar -zxvf " + os.path.join("/cwebs/cwebs.install", packs_distr))	
    except Exception as e:
        print 'can not unpack ', os.path.join("/cwebs/cwebs.install", packs_distr)
	sys.exit()	
    print 'copying into the run folder...'	
    if os.path.exists(os.path.join("/cwebs/cwebs.install", cwebs_distr[:-7])):
        cmd = ss + "cp -r " + "/cwebs/cwebs.install/" + cwebs_distr[:-7] + "/. /cwebs/cwebs/."
	print 'logging: ', cmd
        os.system(ss + "cp -r " + "/cwebs/cwebs.install/" + cwebs_distr[:-7] + "/. /cwebs/cwebs/.") 
	print 'copying...done...'
    else:
        cmd = ss + "cp -r " + "/cwebs/cwebs.install/" + cwebs_distr[:-7] + "/. /cwebs/cwebs/."
	print 'logging: ', cmd
	print 'copying...IS NOT DONE...'
    
    print 'Enter key to proceed with checking out supervisor...'
    raw_input() 
    if os.path.exists("/usr/bin/supervisord"):
       print "supervisord is already installed...exiting"
       print "go and configure"
       sys.exit()
    	
    os.system(ss + "/usr/local/bin/easy_install /cwebs/cwebs.install/cwebs_packages/supervisor-3.0.tar.gz")    
    if not os.path.exists("/etc/supervisor"):
        os.system(ss + "mkdir /etc/supervisor")
    if not os.path.exists("/etc/supervisor/conf.d"):
        os.system(ss + "mkdir /etc/supervisor/conf.d")
    if not os.path.exists("/var/log/supervisor"):
        os.system(ss + "mkdir /var/log/supervisor")
    if not os.path.exists("/etc/init.d/supervisord"):
        os.system(ss + "cp /cwebs/cwebs.install/cwebs_packages/supervisord /etc/init.d/.")
        os.system(ss + "chmod +x /etc/init.d/supervisord")
        os.system(ss + "chkconfig --levels 235 supervisord on") 
    if not os.path.exists("/etc/supervisord.conf"):	
        with open(os.path.join(distr_root, "supervisord.conf"), "w") as conf_file:
	    conf_file.write(supervisord_conf_contents)
        os.system(ss + "mv " + os.path.join(distr_root, "supervisord.conf") + " /etc/.")      

    if not os.path.exists("/etc/supervisor/conf.d/cwebs.conf"):	
        with open(os.path.join(distr_root, "cwebs.conf"), "w") as conf_file:
	    conf_file.write(cwebs_conf_contents)
        os.system(ss + "mv " + os.path.join(distr_root, "cwebs.conf") + " /etc/supervisor/conf.d/.")
	    
	    
    print 'do not forget to start supervisord with'
    print ss + "/etc/init.d/supervisord restart"
