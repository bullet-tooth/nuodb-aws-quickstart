'''
Created on Jan 28, 2014

@author: rkourtz
'''
import nuodbawsquickstart
import inspect, json, os, random, string, sys, time

class Cluster:
    
    def __init__(self, 
                 alert_email = "alert@example.com",
                 aws_access_key = "", 
                 aws_secret = "", 
                 cluster_name = "default",
                 data_dir = "/".join([os.path.dirname(os.path.abspath(inspect.stack()[-1][1])), "data"]), 
                 domain_name="domain", 
                 domain_password="bird", 
                 enable_monitoring = True,
                 instance_type = "m3.xlarge",  
                 ssh_key = "", 
                 ssh_keyfile = None,
                 zones = []):
      args, _, _, values = inspect.getargvalues(inspect.currentframe())
      for i in args:
        setattr(self, i, values[i])
        
      if ssh_keyfile != None and ssh_keyfile != "":
        if not os.path.exists(ssh_keyfile):
          raise Error("Can not find ssh private key %s" % self.ssh_keyfile)
        
      self.zoneconnections = {} #store our zone connections
      for zone in zones:
        self.connect_zone(zone)
      self.db = {"hosts": self.get_existing_hosts()}
    
    def add_host(self, name, zone, ami = "", security_group_ids=[], subnets = [], agentPort = 48004 , subPortRange = 48005, nuodb_rpm_url = None, start_services = True):
      if name not in self.db['hosts']:
        stub= {}
        host_id = len(self.db['hosts'])
        if zone not in self.zoneconnections:
          raise Error("You must connect to a zone first before you can add a host in that zone")
        if len(subnets) == 0:
          raise Error("You must specify the target subnets in an array")
        # make sure ami is valid
        valid_amis = []
        for each_ami in self.zoneconnections[zone].amis:
          valid_amis.append(each_ami.id)
        if ami not in valid_amis:
          raise Error("ami '%s' is not valid" % (ami))
        #common Chef information
        chef_data = {"nuodb": {"is_broker": True, "enableSystemDatabase": True, "autoconsole": {"brokers": ["localhost"]}, "webconsole": {"brokers": ["localhost"]}}}
        chef_data["run_list"] = ["recipe[nuodb]"] 
        chef_data['nuodb']["port"] = agentPort
        chef_data['nuodb']["portRange"] = subPortRange
        chef_data["nuodb"]['automationTemplate'] = "Minimally Redundant"
        chef_data["nuodb"]['balancer'] = "RegionBalancer"
        chef_data["nuodb"]['altAddr'] = "" # Populate this at boot time
        chef_data["nuodb"]['region'] = zone
        if self.alert_email != None and "@" in self.alert_email:
          chef_data["nuodb"]['monitoring'] = {"enable": True, "alert_email": self.alert_email}
        else:
          chef_data["nuodb"]['monitoring'] = {"enable": False, "alert_email": ""}
        chef_data["nuodb"]['domain_name'] = self.domain_name
        chef_data["nuodb"]['domain_password'] = self.domain_password
        chef_data["nuodb"]["start_services"] = True
        if nuodb_rpm_url != None:
          chef_data["nuodb"]["download_url"] = nuodb_rpm_url
        stub['chef_data'] = chef_data
        stub['ami'] = ami
        stub['name'] = name
        stub['region'] = zone
        stub['security_group_ids'] = security_group_ids
        stub['subnet'] = subnets[len(stub) % len(subnets)]
        stub['host'] = nuodbawsquickstart.Host(name, ec2Connection=self.zoneconnections[zone].connection,  
                                               domain = self.domain_name, domainPassword = self.domain_password, 
                                               advertiseAlt = True, region = zone,
                                               agentPort = agentPort, portRange = subPortRange,
                                               isBroker = chef_data['nuodb']['is_broker'], ssh_key = self.ssh_key, ssh_keyfile = self.ssh_keyfile)
        self.db['hosts'][name] = stub
        return stub['host']
      else:
        return self.db['hosts'][name]

    def __boot_host(self, host_id, zone, instance_type = None, wait_for_health = False, ebs_optimized = False):
      if instance_type == None:
        instance_type = self.instance_type
      stub = self.db['hosts'][host_id]
      template_vars = dict(
                          hostname = host_id,
                          chef_json = json.dumps(stub['chef_data']),
                          email_address = self.alert_email
                          )
      f = open("/".join([os.path.dirname(os.path.abspath(inspect.stack()[0][1])), "templates", "init.py"]))
      template = string.Template(f.read())
      f.close()
      userdata = template.substitute(template_vars)
      obj = stub['host'].create(ami=stub['ami'], instance_type=instance_type, security_group_ids=stub['security_group_ids'], subnet = stub['subnet'], getPublicAddress = True, userdata = userdata, ebs_optimized=ebs_optimized)
      print ("Waiting for %s to start" % obj.name),
      while obj.status() != "running":
        print("."),
        time.sleep(5) #Wait 30 seconds in between node starts
      print
      obj.update_data()
      if wait_for_health:
        healthy = False
        count = 0
        tries = 60
        wait = 10
        print "Waiting for agent on %s (%s)" % (obj.name, obj.ext_ip)
        while not healthy or count == tries:
          if obj.agent_running():
            healthy = True
          else:
            print("."),
            time.sleep(wait)
          count += 1
        if not healthy:
          print "Cannot reach agent on %s after %s seconds. Check firewalls and the host for errors." % (obj.name, str(tries * wait))
          exit(1)
        print
        obj.update_data()
      else:
        print "Not waiting for agent on %s, node will come up asynchronously." % obj.name
      return obj
             
    def connect_zone(self, zone):
      self.zoneconnections[zone] = nuodbawsquickstart.Zone(zone)
      self.zoneconnections[zone].connect(aws_access_key=self.aws_access_key, aws_secret=self.aws_secret)
      return self.zoneconnections[zone]
        
    def create_cluster(self, ebs_optimized = False):
      chosen_one = None
      peers = []
      for host_id in self.db['hosts']:
        host = self.get_host(host_id)
        host['chef_data']['nuodb']['brokers'] = peers
        obj = host['host']
        zone = obj.region
        if chosen_one == None:
          # This is the first host
          wait_for_health = True
          chosen_one = self.__boot_host(host_id, zone, wait_for_health = wait_for_health, ebs_optimized = ebs_optimized)
          peers.append(chosen_one.instance.public_dns_name)
          chosen_one.instance.add_tag("nuodbawsquickstart", self.cluster_name)
        else:
          wait_for_health = False
          host['chef_data']['nuodb']['brokers'] = peers
          obj = self.__boot_host(host_id, zone, wait_for_health = wait_for_health, ebs_optimized = ebs_optimized)
          obj.instance.add_tag("nuodbawsquickstart", self.cluster_name)
      
    def delete_db(self):
      self.exit()
      if os.path.exists(self.database_file):
        os.remove(self.database_file)
    
    def delete_dns(self, zone = None):
      if zone == None:
        zones = self.get_zoneconnections()
      else:
        zones = [zone]
      for zone in zones:
        hosts = self.get_hosts(zone=zone)
        for host in hosts:
          host_obj = self.get_host(host)['obj']
          host_obj.dns_delete()
      
    def dump_db(self):
      return self.db
    
    def get_host(self, host_id):
      if host_id in self.db['hosts']:
        return self.db['hosts'][host_id]
      else:
        raise Error("No host found with id of '%s'" % host_id)
    
    def get_host_address(self, host_id):
      return self.db['hosts'][host_id]['host'].instance.public_dns_name
    
    def get_hosts(self):
      return self.db['hosts']
    
    def get_existing_hosts(self, zone=None):
      hosts = {}
      if zone == None:
        for myzone in self.get_zoneconnections():
          for reservation in self.zoneconnections[myzone].connection.get_all_reservations():
            for instance in reservation.instances:
              if hasattr(instance, 'tags') and "nuodbawsquickstart" in instance.tags and instance.tags['nuodbawsquickstart'] == self.cluster_name:
                myhost = {'host': nuodbawsquickstart.Host("", ec2Connection=self.zoneconnections[myzone].connection,  
                                             domain = self.domain_name, domainPassword = self.domain_password, 
                                             instance_id = instance.id,
                                             ssh_key = self.ssh_key, ssh_keyfile = self.ssh_keyfile) }
                hosts[myhost['host'].instance.tags['Name']] = myhost
      else:
        for reservation in self.zoneconnections[zone].connection.get_all_reservations():
          for instance in reservation.instances:
            if hasattr(instance, 'tags') and "nuodbawsquickstart" in instance.tags and instance.tags['nuodbawsquickstart'] == self.cluster_name:
              myhost = {'host': nuodbawsquickstart.Host("", ec2Connection=self.zoneconnections[myzone].connection,  
                                           domain = self.domain_name, domainPassword = self.domain_password, 
                                           instance_id = instance.id,
                                           ssh_key = self.ssh_key, ssh_keyfile = self.ssh_keyfile) }
              hosts[myhost['host'].instance.tags['Name']] = myhost
      return hosts
    
    def get_zoneconnections(self):
      return sorted(self.zoneconnections)
      
    def terminate_hosts(self, zone = None):
      hosts = self.get_existing_hosts(zone)
      for host in hosts:
        host_obj = hosts[host]['host']
        if host_obj.exists and host_obj.instance._state.code == 16:
          print "Terminating %s" % host_obj.name
          host_obj.terminate()
     
class Error(Exception):
  pass 

class Unbuffered(object):
  def __init__(self, stream):
    self.stream = stream
  def write(self, data):
    self.stream.write(data)
    self.stream.flush()
  def __getattr__(self, attr):
    return getattr(self.stream, attr)

