nuodb-aws-quickstart
====================

Toolkit to start a multi-region NuoDB cluster in Amazon Web Services

#### Using `nuodb_aws_quickstart.py`:
* This script will, based on your answers to a few questions, automatically spin up a customized NuoDB domain in [Amazon EC2](http://aws.amazon.com/ec2/)

#### Before you start
  * OSX
    * Install XCode (App Store -> xcode)
    * Install Python's [setuptools](https://pypi.python.org/pypi/setuptools#unix-including-mac-os-x-curl) (Terminal -> `curl https://bootstrap.pypa.io/ez_setup.py -o - | sudo python`)
  * Fedora, CentOS, RHEL
    * `sudo yum -y install gcc git python-devel python-pip`
  * Ubuntu
    * `sudo apt-get install gcc git python-dev python-pip`

#### What you need to know:
  * The script will prompt you for:
    * Whether to create a new domain, or terminate an existing one
    * The name of the cluster
  * When creating a cluster, you'll need to provide:
    * A password to use for the new NuoDB domain
    * An email address to send error notifications. Provide a blank response if none desired.
    * AWS credentials
     * You should know your AWS access key and AWS secret key. See the [AWS IAM](AWS_IAM.md) page for help on setting up your account in AWS.
    * AWS Regions
     * AWS offers multiple regions. You should determine which regions you wish to use for your cluster. A single region is sufficient, but for geo-distribution you'll want to configure more than one.
     * You'll need to know the AWS region "code" for each region you'd like to use. See the list of AWS regions and their codes [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html).
     * You should have a keypair that exists in each region. See the [AWS IAM](AWS_IAM.md) page for details.
    * The script will confirm before creating a security zone in each region for you. This security zone will contain the following ports open to the world:
     * 22 (SSH) - for you to SSH in after the instances have been started
     * 8080, 8888, 9001, 48004-48020 (NuoDB ports)


  
#### Installation & Execution
* Download the latest [release](https://github.com/nuodb/aws-quickstart/releases) of this repository to your local machine and extract it.
* In the directory you just created run
`python setup.py install`
* Run `nuodb_aws_quickstart.py`
* Enter the data gathered in the "What you need to know" section above when prompted by the script
* When the script completes you will have a running NuoDB domain in your AWS account. The script will provide you with a URL for the NuoDB Admin Center for the new domain so that you may start interacting with it immediately.
* If you run into any issues check the [troubleshooting page](Troubleshooting.md)
