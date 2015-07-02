#!/usr/bin/python

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import nuodbawsquickstart
import json
import os
import ssl
import sys
import time
import unicodedata
import urllib2

INSTANCE_TYPE = "m4.xlarge"
NUODB_DOWNLOAD_URL = "http://download.nuohub.org/nuodb-%s.x86_64.rpm"

def save_config(config, file):
  with open(file, 'wt') as f:
    f.write(json.dumps(config, indent=4, sort_keys=True))
    
def user_prompt(prompt, valid_choices = [], default = None):
  if default != None:
    prompt = "%s [%s] " % (prompt, str(default))
  val = raw_input(prompt).strip()
  if len(valid_choices) == 0:
    if default == None:
      return val
    else:
      return default
  for choice in valid_choices:
    if val == str(choice):
      return choice
  valid_strings = []
  #Handle integer inputs
  for choice in valid_choices:
    valid_strings.append(str(choice))
  print "Invalid choice. Your choices are: [" + ",".join(valid_strings) + "]"
  return user_prompt(prompt, valid_choices)
  
def choose_from_list(params = [], suggested = None):
  # returns index of the list you gave me
  i = 0
  options = []
  while i < len(params):
    if suggested != None and suggested == i:
      suggest_prompt = "<----- SUGGESTED"
    else:
      suggest_prompt = ""
    #print "%s)  %s %s" % (i+1, params[i], suggest_prompt)
    print '{:2d}) {:25} {}'.format(i+1, params[i], suggest_prompt)
    i += 1
    options.append(i)
  return user_prompt("Choose one:", options) - 1

def choose_multiple_from_list(params = []):
  # returns list of indicies from parameters sent
  tally = []
  while True:
    list_to_send = []
    for idx, param in enumerate(params):
      if idx not in tally:
        list_to_send.append(param)
    if len(list_to_send) == 0:
      return tally
    else:
      list_to_send.append("DONE CHOOSING")
      result = choose_from_list(list_to_send)
      if result == len(list_to_send) - 1:
        return tally
      else:
        choice = list_to_send[result]
        for idx, param in enumerate(params):
          if choice == param:
            tally.append(idx)

def get_instance_type(c):
  return INSTANCE_TYPE
  
def get_regions(c):
  regions = []
  for region in nuodbawsquickstart.Zone("us-east-1").connect(c["aws_access_key"], c["aws_secret"]).get_all_regions():
    regions.append(region.name)
  return regions
  
def get_zone_info(c):
  # Find our how many regions
  r = {}
  available_zones = get_regions(c)
  zonecount = len(available_zones)
  zone_count_prompt = user_prompt("How many AWS regions? (1-%i)? " % zonecount, range(1,zonecount + 1))
  if zone_count_prompt == str(zonecount):
    for zone in available_zones:
      r[zone] = {}
  else:
    i = 0
    while i < int(zone_count_prompt):
      regionlist = []
      for zone in available_zones:
        if zone not in r:
          regionlist.append(zone)
      get = int(choose_from_list(sorted(regionlist)))
      r[sorted(regionlist)[get]] = {}
      i += 1
  # amazon has a ton of amis named the same thing. Choose the latest one. Only reliable way I can find is to scrape their wiki. Cache this.
  page_cache = unicodedata.normalize("NFKD", unicode(urllib2.urlopen("http://aws.amazon.com/amazon-linux-ami/").read(), "utf-8"))
  for region in r:
    # Server count 
    r[region]["servers"] = user_prompt(region + " --- How many servers? (1-20) ", range(1,20))
    zone_obj = nuodbawsquickstart.Zone(region)
    zone_conn = zone_obj.connect(c["aws_access_key"], c["aws_secret"])
    
    # Validate SSH Key
    
    keypairs = zone_conn.get_all_key_pairs()
    keynames = []
    if len(keypairs) == 0:
      print "Cannot find any key pairs in region %s. Please add a keypair to this region and then re-run this script." % region
      sys.exit(2)
    for keypair in keypairs:
      keynames.append(keypair.name)
    print region + " --- Choose a keypair:"
    r[region]['keypair'] = keynames[choose_from_list(keynames)]
    
    # Choose AMI
    print region + " --- Determining AMIs (Loading...) "
    amis = zone_obj.amis
    ami_dict = {}
    suggested = None
   
    for ami in amis:
      if ami.architecture == "x86_64" and ami.description != None and len(ami.description) > 0 and "ami-" in ami.id and ami.platform != "windows":
        if ami.owner_alias != None:
          if ami.owner_alias.encode('utf-8') == u"amazon" and ami.id in page_cache:
            ami_dict["  ".join([ami.id.encode('utf-8'), ami.description.encode('utf-8')])] = {"id": ami.id, "location": ami.location}
          elif ami.owner_alias.encode('utf8') != u"amazon": 
            ami_dict["  ".join([ami.id.encode('utf-8'), ami.description.encode('utf-8')])] = {"id": ami.id, "location": ami.location}
    ami_descriptions = sorted(ami_dict.keys()) 
    ami_descriptions.append("NONE OF THE ABOVE")
    chosen_ami = None
    for idx, desc in enumerate(ami_descriptions):
      if "HVM GP2" in desc:
        chosen_ami =  ami_dict[desc]['id']
        suggested = idx
        r[region]["ami"] = chosen_ami
    if chosen_ami == None:
      ami_choice = choose_from_list(ami_descriptions, suggested)
      if ami_choice == len(ami_descriptions) - 1:
        print region + " --- Choose the AMI (Loading...) "
        ami_enter = ""
        while "ami-" not in ami_enter:
          ami_enter = user_prompt("Enter the AMI you want to use (ami-xxxxxxxx): ")
        r[region]["ami"] = ami_enter
      else:
        r[region]["ami"] =  ami_dict[ami_descriptions[ami_choice]]['id']
    
    #What subnets to use?
    print region + " --- Finding subnets... "
    if 'zones' in region and region in c['zones'] and "subnets" in c['zones'][region] and len(c['zones'][region]['subnets']) > 0 and "vpcs" in c['zones'][region]:
      r[region]['subnets'] = c['zones'][region]['subnets']
      r[region]['vpcs'] = c['zones'][region]['vpcs']
    else:
      subnets = zone_obj.get_subnets()
      possibilities = {}
      r[region]['subnets'] = None
      for subnet in subnets:
        if subnets[subnet]['state'] == "available":
          possibilities[subnets[subnet]['id']] = subnets[subnet]
          if subnets[subnet]['defaultForAz'] == "true":
            r[region]['subnets'] = [subnets[subnet]['id']]
            r[region]['vpcs'] = [subnets[subnet]['vpc_id']]
      if r[region]['subnets']==  None:
        print "ERROR: Could not automatically determine default subnet in region %s. Please choose one:" % region
        choice = choose_from_list(possibilities.keys())
        id= possibilities.keys()[choice]
        r[region]['subnets'] = [possibilities[id]['id']]
        r[region]['vpcs'] = [possibilities[id]['vpc_id']]
    
    #What security groups to use?
    r[region]['security_group_ids'] = []
    my_security_group = None
    for group in zone_obj.get_security_groups():
      if group.name == "NuoDB_default_ports" and group.vpc_id in r[region]['vpcs']:
        my_security_group = group.id
    if my_security_group == None:
      res = user_prompt("I am going to create a security group in region %s. It would open the default NuoDB ports and SSH to all IPs. Is this OK? (y/n)" % region, ["y", "n"], "n")
      if res =="y":
        sg = zone_obj.edit_security_group("NuoDB_default_ports", "These are the default NuoDB ports, open to the world. Autogenerated by nuodb.nuodb_demo_storefront_setup", [{"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_ip": "0.0.0.0/0"}, {"protocol": "tcp", "from_port": 48004, "to_port": 48020, "cidr_ip": "0.0.0.0/0"}, {"protocol": "tcp", "from_port": 8888, "to_port": 8889, "cidr_ip": "0.0.0.0/0"}, {"protocol": "tcp", "from_port": 8080, "to_port": 8080, "cidr_ip": "0.0.0.0/0"}, {"protocol": "tcp", "from_port": 9001, "to_port": 9001, "cidr_ip": "0.0.0.0/0"}], r[region]['vpcs'][0])
        my_security_group = sg.id
      else:
        print "Cannot continue without a security group. Exiting."
        sys.exit()
    r[region]['security_group_ids'] = [my_security_group]

  return r 

#### Create a cluster

def help():
  print "%s create" % sys.argv[0]
  print "%s terminate" % sys.argv[0]

def validate_download(url):
  try:
    urllib2.urlopen(url)
    return True
  except:
    return False
  
  
def __main__(cmdargs = None):
  config_file = "./config.json"
  
  if cmdargs.action == "create":
    params = {
            "cluster_name": { "default" : "NuoDBQuickstart", "prompt" : "What is the name of your cluster?"},
            "aws_access_key": {"default" : "", "prompt" : "What is your AWS access key?"},
            "aws_secret": {"default" : "", "prompt" : "What is your AWS secret?"},
            "domain_password": {"default": "bird", "prompt": "What is the admin password of your NuoDB domain?"},
            "alert_email" : {"default" : "","prompt" : "What email address would you like health alerts sent to?"},
          }
    #### Gather all the data we need
    c = {}
    if os.path.exists(config_file):
      with open(config_file) as f:
        static_config = json.loads(f.read())
        f.close()
    else:
      static_config = {}
      
    for key in static_config:
      if key in params:
        params[key]['default'] = static_config[key]
    
    for key in sorted(params.keys()):
      #if len(str(params[key]['default'])) > 30:
      #  default = str(params[key]['default'])[0:27] + "..."
      #else:
      default = str(params[key]['default'])
      val = raw_input("%s [%s] " % (params[key]['prompt'], default)).strip()
      if len(val) == 0:
        c[key] = params[key]['default']
      else:
        c[key] = val
      save_config(c, config_file)

    #### Get Instance type
    if hasattr(cmdargs, "instancetype") and cmdargs.instancetype != "DEFAULT":
      c['instance_type'] = cmdargs.instancetype
    else:
      c['instance_type'] = get_instance_type(c)
    save_config(c, config_file)
      
    if hasattr(cmdargs, "nuodbVersion") and cmdargs.nuodbVersion != "DEFAULT":
      if validate_download(NUODB_DOWNLOAD_URL % cmdargs.nuodbVersion):
        c['nuodb_version'] = cmdargs.nuodbVersion
      else:
        print "Can't find NuoDB version %s on the public download server. Please check the version and try again." % cmdargs.nuodbVersion
        sys.exit(2)  
    else:
      c['nuodb_version'] = None
      
    c['domain_name'] = "domain"
    save_config(c, config_file)
    c["zones"] = get_zone_info(c)
      
    print "Saving this information for later to %s" % config_file
    save_config(c, config_file)
    
    
    #######################################
    #### Actually do some work
    #######################################
    
    mycluster =  nuodbawsquickstart.Cluster(
                                           alert_email = c['alert_email'],
                                           aws_access_key = c['aws_access_key'], aws_secret = c['aws_secret'], 
                                           cluster_name = c['cluster_name'], domain_name = c['domain_name'],
                                           domain_password = c['domain_password'], instance_type = c['instance_type'],
                                           nuodbVersion = c['nuodb_version'])
    print "Creating the cluster."
    count = 0
    for zone in c['zones']:
      mycluster.connect_zone(zone)
      z = c['zones'][zone]
      for i in range(0,z['servers']):
        root_name = "%s-%i" % (c['cluster_name'], count)
        myserver = mycluster.add_host(name=root_name, zone=zone, ami=z['ami'], subnets=z['subnets'], security_group_ids = z['security_group_ids'], keypair = z['keypair']) # Mark the number of nodes to be created
        print "Added %s (%s)" % (root_name, myserver.region)
        count += 1
    
    print "Booting the cluster"
    mycluster.create_cluster() # Actually spins up the nodes.
    hosts = mycluster.get_hosts()
    
    print("Waiting for an available web console")
    healthy = False
    i=0
    wait = 600 #seconds
    good_host = None
    while i < wait:
      if not healthy:
        for host_id in hosts:
          obj = mycluster.get_host(host_id)['host']
          address = mycluster.get_host_address(host_id)
          url = "http://%s:%s" % (address, obj.autoconsole_port)
          if not healthy:
            try:
              urllib2.urlopen(url, None, 2)
              good_host = url
              healthy = True
            except:
              pass
        time.sleep(1)
      i += 1
    if not healthy:
      print "Gave up trying after %s seconds. Check the server" % str(wait)
    else:
      print
      print "########################################################################################"
      print "You can now access the NuoDB Admin Center (Username: domain Password: %s) at" % c['domain_password']
      print str(good_host)
      print "where you'll find documentation, samples and demos (check out Storefront!)"
      print "and the Automation Console (create and manage databases)."
      print "Other instances in the cluster may still be booting and will join the cluster over time."
      print "########################################################################################"
      print
    
  ########################
  #### Terminate a cluster
  ########################
  elif cmdargs.action == "terminate":
    if os.path.exists(config_file):
      with open(config_file) as f:
        c = json.loads(f.read())
        f.close()
    else:
      c = {}
      params = {
            "cluster_name": { "default" : "NuoDBQuickstart", "prompt" : "What is the name of your cluster?"},
            "aws_access_key": {"default" : "", "prompt" : "What is your AWS access key?"},
            "aws_secret": {"default" : "", "prompt" : "What is your AWS secret?"},
          }
      for key in sorted(params.keys()):
      #if len(str(params[key]['default'])) > 30:
      #  default = str(params[key]['default'])[0:27] + "..."
      #else:
        default = str(params[key]['default'])
        val = raw_input("%s [%s] " % (params[key]['prompt'], default)).strip()
        if len(val) == 0:
          c[key] = params[key]['default']
        else:
          c[key] = val
      
    mycluster =  nuodbawsquickstart.Cluster(
                                           alert_email = "",
                                           aws_access_key = c['aws_access_key'], aws_secret = c['aws_secret'], 
                                           cluster_name = c['cluster_name'], domain_name = "",
                                           domain_password = "", instance_type = "")
    for zone in get_regions(c):
      mycluster.connect_zone(zone)
    mycluster.terminate_hosts()
  else:
    help()

if hasattr(ssl, '_create_unverified_context'):
  ssl._create_default_https_context = ssl._create_unverified_context
  
program_license = ""
parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
parser.add_argument("--nuodbVersion", dest="nuodbVersion", help="Which version of NuoDB to use [default: %(default)s]", default="DEFAULT", required=False)
parser.add_argument("--instancetype", dest="instancetype", help="Which type of AWS instance to use [default: %s]"  % INSTANCE_TYPE, default="DEFAULT", required=False)
parser.add_argument("action", help="What action do you want to take on the cluster? (create/terminate)", nargs="?")
args = parser.parse_args()
if args.action not in ["create", "terminate"]:
  res = user_prompt("What action do you want to take on the cluster? (create/terminate): ", ["create", "terminate"])
  args.action = res.strip()
__main__(cmdargs = args)
