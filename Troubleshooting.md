### Troubleshooting
* ERROR: `Unable to connect to AWS zone us-east-1 with credentials provided. Please check the credentials and try again.`
  * Check to make sure the credentials you entered are correct.
* ERROR: `You are not authorized to perform this operation.` 
  * Make sure your user has the [right credentials](IAM_AWS.md#IAM) for EC2
* ERROR: `Cannot find any key pairs in region XXXXX. Please add a keypair to this region and then re-run this script.`
  * Make sure you have a [public/private key pair](IAM_AWS.md#keypairs) in each region
  