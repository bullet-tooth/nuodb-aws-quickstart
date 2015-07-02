#!/usr/bin/python
import subprocess
import json, os, time, urllib2

print "Starting cloud-init from userdata"

packages = ["git","mailx"]

commands = [
            #"hostname $hostname",
            
            #"yum -y install https://opscode-omnibus-packages.s3.amazonaws.com/el/6/x86_64/chef-11.8.2-1.el6.x86_64.rpm",
            "curl -L https://www.chef.io/chef/install.sh | bash",
            "mkdir -p /var/chef/cookbooks",
            "mkdir -p /etc/yum.repos.d",
            "sed -i \"s/127\.0\.0\.1.*/127.0.0.1 localhost localhost.localdomain `hostname`/g\" /etc/hosts"
            ]

git_repos = {"nuodb": "https://github.com/nuodb/nuodb-chef.git",
             "java": "https://github.com/socrata-cookbooks/java",
             "yum-epel": "https://github.com/opscode-cookbooks/yum-epel.git",
             "yum": "https://github.com/opscode-cookbooks/yum.git"
             }
for repo in git_repos:
  commands.append("if [ ! -d /var/chef/cookbooks/%s ]; then git clone %s /var/chef/cookbooks/%s; fi;" % (repo, git_repos[repo], repo))
  commands.append("cd /var/chef/cookbooks/%s && git pull" % repo)

def execute(command):
  print "Running \"%s\"" % command
  p = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = p.communicate()
  print "Returncode: %i" % p.returncode
  print "STDOUT: %s" % stdout
  print "STDERR: %s" % stderr
  return (p.returncode, stdout, stderr)

def get_public_hostname():
  url = "http://169.254.169.254/latest/meta-data/public-hostname"
  return urllib2.urlopen(url).read()

def mail(destination = "$email_address", msg = "", subject = "Failure starting host %s" % get_public_hostname()):
  command = "echo %s | mail -s %s %s" % (msg, subject, destination)
  execute(command)

# Install Packagaes
# Determine our package manager 
methods = { 
           "zypper": "zypper install -y",
           "apt-get": "apt-get -y install",
           "yum": "yum -y install"
}
install_command = None
for method in methods.keys():
  if execute("which %s" % method)[0] == 0:
    install_command = methods[method]
if install_command == None:
  install_command = methods["yum"]

for package in packages:
  command = " ".join( [install_command, package])
  count = 1
  while count <= 18:
    (rc, stdout, stderr) = execute(command + " # Attempt %i" % count)
    if rc == 0:
      break
    time.sleep(10)
    count += 1

for command in commands:
  (rc, stdout, stderr) = execute(command)
  # ignore errors
  
ohai = json.loads(execute("/usr/bin/ohai")[1])
public_address = get_public_hostname()
#if execute("grep -c $hostname /etc/hosts")[0] != 0:
#    f = open("/etc/hosts", "a")
#    f.write("\t".join([public_address, "$hostname" + "\n"]))
#    f.close()
print "Setting Chef Data"
chef_data = json.loads('$chef_json')
chef_data['nuodb']['altAddr'] = public_address
chef_data['nuodb']['autoconsole']['brokers'] = [public_address]
f = open("/var/chef/data.json", "w")
f.write(json.dumps(chef_data))
f.close()
print "Running Chef... outputting to /var/log/chef.log"
(chef_result, chef_stdout, chef_stderr) = execute("chef-solo -j /var/chef/data.json | tee -a /var/log/chef.log")
print "Chef run complete. Output in /var/log/chef.log"
if chef_result != 0:
  mail(msg="\n".join([chef_stdout, chef_stderr]))