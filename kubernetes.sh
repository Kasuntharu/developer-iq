curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
echo "EKSCTL intalled"

sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
echo "Kubectl installed"

kubectl version --client > $version
echo "$version"

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
echo "awscli installed"

ARCH=amd64
PLATFORM=$(uname -s)_$ARCH
curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"


echo "extracting"
tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz

echo "Move to the binary folder"
sudo mv /tmp/eksctl /usr/local/bin

echo "-----------Done----------"

rm -rf ./aws ./awscliv2.zip ./kubectl