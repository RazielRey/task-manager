#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "===== User Data Script Started ====="
date

echo "Updating system..."
apt-get update -y
apt-get upgrade -y

echo "Installing required packages..."
apt-get install -y curl wget git python3 python3-pip

echo "Installing Docker..."
curl -fsSL https://get.docker.com | sh
usermod -aG docker ubuntu

echo "Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
mv kubectl /usr/local/bin/

echo "installing AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
apt-get install -y unzip
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

echo "Cleaning up..."
apt-get clean

echo "===== User Data Script Completed Successfully ====="
date

