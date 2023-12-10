# developer-iq
## sub 
Track productivity of Developer
App for track developer productivity

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

eksctl create cluster  --region ap-southeast-1 --node-type t3.small  --nodes 2  --nodes-min 1  --nodes-max 4 --name dev-iq-cluster-dumi --kubeconfig= /workspace/developer-iq

----


aws eks update-kubeconfig --region ap-southeast-1 --name dev-iq-cluster-dumi

---set environment variable

set KUBECONFIG= /workspace/developer-iq/kube-config.yaml

----run deployment file
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

-----roleout deployment
kubectl set image deployment/my-app my-app=my-app:new-version --record
kubectl rollout status deployment/californiavoters-app
kubectl rollout undo deployment/californiavoters-app
kubectl rollout pause deployment/californiavoters-app
kubectl rollout resume deployment/californiavoters-app


kubectl get deploy && kubectl get rs && kubectl get pod && kubectl get svc

kubectl delete deployments --all
kubectl delete pods --all
kubectl delete services --all


kubectl delete deployments --all && kubectl delete pods --all && kubectl delete services --all

- name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build, tag, and push the image to Amazon ECR
      id: build-image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: ${{ secrets.REPO_NAME }}
        IMAGE_TAG: "latest"

      run: |
        # Build a docker container and push it to ECR 
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        echo "Pushing image to ECR..."
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        echo "::set-output name=image::$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"


