### Troubleshooting
* `Unable to connect to AWS zone us-east-1 with credentials provided. Please check the credentials and try again.`
  * Check to make sure the credentials you entered are correct.
  * `You are not authorized to perform this operation.` 
    * The credentials you entered do not have sufficient permissions to perform these actions.
    * In the IAM console click on your username and then "Attach User Policy"
    * Select "Amazon EC2 Full Access" and apply this policy.
* `Cannot find any key pairs in region XXXXX. Please add a keypair to this region and then re-run this script.`
  * When starting an EC2 instance you need a public/private keypair for SSHing in to the instance. Amazon stores the public part of the keypair and adds it to the instance at boot time. 
  * This script does not need command line access to configure the hosts but it does need to know what Amazon calls the keypair.
  * To create a new keypair in a region go the AWS Web UI -> EC2 -> Select the region in the upper right -> Key Pairs -> Create Key Pair
  
  