### Setting up your AWS account for use with this toolkit

<a href="#IAM" />
##### IAM (Identity and Access Management):
This script requires a user in your AWS account with the credentials to be able to start and stop instances, create security groups, and see the public RSA keys stored in your account.
* In the [AWS Web UI](https://console.aws.amazon.com/iam/home?#home) click on `Services` -> `IAM`
* On the left select `Users`
* `Create New Users`
* Enter a username for your new account - like "NuoDB"
* Make sure "Generate an access key for each user" is checked
* When the "Access Key ID" and "Secret Access Key" are shown to you copy them to a location you can access later. If you lose the "Secret Access Key" you will have to recreate the key pair.
* When back at the page that shows you a list of users click on the username you just created
* Click on `Attach User Policy`
* Select "Amazon EC2 Full Access"
* `Apply Policy`

<a href="#keypairs" />
##### Keypairs
Keypairs are public/private key pairs used to log into your instances. Each region you are going to start instances in requires at least one keypair.
* To create a keypair in a region
  * Click on `Services` -> `EC2` -> `Key Pairs`
  * To create a new key pair click on `Create Key Pair`
    * Enter a name for your keypair
    * Your browser will download a "pem" file. This is your private key. Store it in a safe place - you will need it to SSH into your machines later.
  * If you have an existing public/private pair then follow the prompts to `Import Key Pair`

