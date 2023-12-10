# developer-iq
## sub 
Application for tracking developer productivity using Gihub REST API

## Development setup
Run Below in root
\
`pip install -r requirements.txt`
\
`python main.py`

\
### To run inside each microservice
\
`uvicorn main:app --port 8001 --reload`

### Below environment variables should set before starting the microservices
- AWS_ACCESS_KEY
- AWS_SECRET_KEY
- AWS_REGION
- GITHUB_USERNAME
- GITHUB_ACCESS_TOKEN

### Base64 encoding
encoding should be done before setting env variables to secrets.yaml
`echo -n text-to-encode | base64`

### Install kubectl
```curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"```

`sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl`

`kubectl version --client`


### Install aws-cli
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

### Install eksctl
ARCH=amd64
PLATFORM=$(uname -s)_$ARCH
curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"

tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz

sudo mv /tmp/eksctl /usr/local/bin

### Create EKS cluster

eksctl create cluster  --region ap-southeast-1 --node-type t3.small  --nodes 2  --nodes-min 1  --nodes-max 4 --name dev-iq-cluster-dumi --kubeconfig=/workspace/developer-iq/kube-config.yaml

----


aws eks update-kubeconfig --region ap-southeast-1 --name dev-iq-cluster-dumi

---set environment variable

set KUBECONFIG=/workspace/developer-iq/kube-config.yaml

----run deployment file
kubectl apply -f app-secrets.yaml

kubectl apply -f dumi-deployment-loadbalancer.yaml

kubectl apply -f /workspace/developer-iq/deployment.yaml

----update
kubectl config set-context --current --namespace=dev-iq

---get namespaces
kubectl get namespaces

---get running nodes
kubectl get nodes

---get services
kubectl get svc

---get pods
kubectl get pods

---get deployments
kubectl get deployments

---describe deployments
kubectl describe deployments


--aws load balancer controller install guide
https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html

kubectl get deploy && kubectl get rs && kubectl get pod && kubectl get svc

kubectl delete deployments --all
kubectl delete pods --all
kubectl delete services --all
kubectl delete deployments --all && kubectl delete pods --all && kubectl delete services --all


### delete the EKS cluster
eksctl delete cluster --name dev-iq-cluster-dumi --region ap=southeast-1

### redeploy
kubectl rollout restart deployment/getmetricsservice
kubectl rollout restart deployment/postmetricsservice
