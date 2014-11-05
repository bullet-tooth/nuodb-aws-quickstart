nuodb-aws-quickstart
====================

Scripts to start a multi-region NuoDB cluster in Amazon Web Services

#### Using `nuodb_aws_quickstart.py`:
* This script allows you to spin up the necessary services to run a NuoDB cluster in [Amazon EC2](http://aws.amazon.com/ec2/)

#### Prerequisites
  * OSX
    * Install XCode (App Store -> xcode)
    * Install Python's [setuptools](https://pypi.python.org/pypi/setuptools#unix-including-mac-os-x-curl) (Terminal -> `curl https://bootstrap.pypa.io/ez_setup.py -o - | sudo python`)
  * Fedora, CentOS, RHEL
    * `sudo yum -y install gcc git python-devel python-pip`
  * Ubuntu
    * `sudo apt-get install gcc git python-dev python-pip`

#### Preparation:
  * Amazon has (as of this writing) 9 different regions. You should determine which regions you wish to use for your cluster. A single region is sufficient, but for georedundancy you may want to run in more than one region simultaneously.
  * You should have a keypair that exists in each region. This is necessary for ssh access to the host.
  * This script has the ability to auto-create a security zone for you. This security zone will contain the following ports open to the world:
    * 22 (SSH) - for you to SSH in after the instances have been started
    * 8080, 8888, 9001, 48004-48020 (NuoDB ports)
  * AWS credentials
    * You should know your AWS access key and AWS secret key. They can be generated from the AWS [IAM](https://console.aws.amazon.com/iam/home?region=us-east-1#users) module 
  
#### Installation & Execution
* Download the latest [release](https://github.com/nuodb/aws-quickstart/releases) of this repository to your local machine and extract it.
* In the directory you just created run
`python setup.py install`
* Run `nuodb_aws_quickstart.py`
* Enter the information you gathered above, following the prompts
* When the script completes you will have a running cluster in AWS. The script will provide you with URLs for the consoles and brokers so that you may start interacting with it immediately.
* If you run into any issues check the [troubleshooting page](Troubleshooting.md)
