import boto.ec2
import inspect, time

class Host:
  def __init__(self, 
               name, 
               ec2Connection = None, 
               autoconsole_port = "8888",
               instance_id = None,
               isBroker = False, 
               ssh_key = None, # Name of AWS Keypair
               region = "default",
               web_console_port = "8080"):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    for i in args:
      setattr(self, i, values[i])
    self.exists = False

    for reservation in self.ec2Connection.get_all_reservations():
      for instance in reservation.instances:
        if self.instance_id != None and instance.id == self.instance_id:
          self.exists = True
          self.instance = instance
          self.name = instance.tags['Name']
          self.zone = instance._placement
          self.id = instance_id
          self.update_data()
        if "Name" in instance.__dict__['tags'] and instance.__dict__['tags']['Name'] == name and (instance.state == 'running' or instance.state == 'pending'):
          self.exists = True
          self.instance = instance
          self.zone = instance._placement
          self.update_data()
        
  def __getitem__(self, attr):
    return getattr(self, attr)

  def create(self, ami, instance_type, getPublicAddress=False, security_group_ids=None, subnet=None, userdata = None, ebs_optimized = False):
    if not self.exists:
      if userdata != None:
        self.userdata = userdata
      if subnet == None: 
        #interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id=subnet, groups=security_group_ids)
        interface_collection = None
      else:
        interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id=subnet, groups=security_group_ids, associate_public_ip_address=getPublicAddress)
        interface_collection = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)
      if instance_type != "t1.micro" and self.ec2Connection.get_image(ami).root_device_type !='instance-store':
        xvdb = boto.ec2.blockdevicemapping.BlockDeviceType()
        xvdb.ephemeral_name = 'ephemeral0'
        bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
        bdm['/dev/xvdb'] = xvdb
      else:
        bdm = None
      if interface_collection != None:
        reservation = self.ec2Connection.run_instances(ami, key_name=self.ssh_key, instance_type=instance_type, user_data=userdata, network_interfaces=interface_collection, ebs_optimized=ebs_optimized, block_device_map=bdm)
      else:
        reservation = self.ec2Connection.run_instances(ami, key_name=self.ssh_key, instance_type=instance_type, user_data=userdata, security_group_ids=security_group_ids, ebs_optimized=ebs_optimized, block_device_map=bdm) 
      self.exists = True
      for instance in reservation.instances:
        self.instance = instance
        self.update_data()
        self.zone = instance._placement
        instance.add_tag("Name", self.name)
      return self
    else:
      print("Node " + self.name + " already exists. Not starting again.")
      self.update_data()
      return self
      
  def status(self):
    try:
      self.update_data()
      return self.instance.state
    except:
      return "Host does not exist"
          
  def terminate(self):
    if self.exists:
      # self.dns_delete()
      self.ec2Connection.terminate_instances(self.id)
      self.exists = False
      return(True, "Terminated " + self.name)
    else:
      return(False, "Cannot terminate " + self.name + " as node does not exist.")
          
  def update_data(self):
    good = False
    count = 0
    while not good and count < 5:
      try:
        self.instance.update()
        self.id = self.instance.id
        self.ext_ip = self.instance.ip_address
        self.int_ip = self.instance.private_ip_address
        return True
      except:
        time.sleep(5)
        count += 1
    return False
        
class HostError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return self.value        