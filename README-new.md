# Developer-iq Run Book
Application for tracking developer productivity using Gihub REST API (Recomended for using a linux environment)

## Development setup

#### Clone the Repository using git client

`git clone https://github.com/Kasuntharu/developer-iq.git`

#### Create a virtual environment python
`python -m venv dev-iq`

#### Install the requirement.txt
`pip install -r requirements.txt`

Follow the link ```https://fastapi.tiangolo.com/``` for further referance

### Below environment variables should set before starting the microservices
- AWS_ACCESS_KEY
- AWS_SECRET_KEY
- AWS_REGION
- GITHUB_USERNAME
- GITHUB_ACCESS_TOKEN


### To run inside each microservice after navigating in to each microservices

`uvicorn main:app --port 8001 --reload`
`uvicorn main:app --port 8002 --reload`



#### Base64 encoding
encoding should be done before setting env variables to app-secrets.yaml
`echo -n text-to-encode | base64`


### Install kubectl
`curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"`

`sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl`

`kubectl version --client`


### Install aws-cli
`curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install`


### Install eksctl
`ARCH=amd64`

`PLATFORM=$(uname -s)_$ARCH`

`curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"`

`tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz`

`sudo mv /tmp/eksctl /usr/local/bin`


### Set aws credentials
 `aws configure`


### Create EKS cluster (Run only one time)

`eksctl create cluster  --region ap-southeast-1 --node-type t3.small  --nodes 2  --nodes-min 1  --nodes-max 4 --name dev-iq-cluster-dumi --kubeconfig=/workspace/developer-iq/kube-config.yaml`



### Update Kubeconfig for AWS EKS:
`aws eks update-kubeconfig --region ap-southeast-1 --name dev-iq-cluster-dumi`


### Set environment variables
`set KUBECONFIG=/workspace/developer-iq/kube-config.yaml`

### Applying the secret file 
`kubectl apply -f app-secrets.yml`


### Applying the deployment file 
`kubectl apply -f dumi-deployment-loadbalancer.yaml`


## Getting Cluster Information:
#### Get namespaces
`kubectl get namespaces`

#### Get running nodes
`kubectl get nodes`

#### Get services
`kubectl get svc`

#### Get pods
`kubectl get pods`

#### Get deployments
`kubectl get deployments`

#### Describe deployments
`kubectl describe deployments`

#### Getting Error Logs
`kubectl logs -f postmetricsservice-8649d85d66-8mplk`

##### All in one
`kubectl get deploy && kubectl get rs && kubectl get pod && kubectl get svc`

### Deleting Deployments, Pods, and Services:
`kubectl delete deployments --all`

`kubectl delete pods --all`

`kubectl delete services --all`

`kubectl delete deployments --all && kubectl delete pods --all && kubectl delete services --all`


### Delete the EKS cluster in a case of faliure 
`eksctl delete cluster --name dev-iq-cluster-dumi --region ap=southeast-1`

### Redeployment (Demonstrate CI/CD Architecture):
`kubectl rollout restart deployment/getmetricsservice`

`kubectl rollout restart deployment/postmetricsservice`


## MISC

#### AWS load balancer controller install guide
https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html

### Test