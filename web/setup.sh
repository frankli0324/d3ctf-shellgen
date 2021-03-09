#!/bin/sh

# install docker first...
apt update
apt install -y apt-transport-https ca-certificates curl gnupg
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" |
    sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
apt install -y docker-ce docker-ce-rootless-extras slirp4netns

# add container user

adduser --gecos "" --disabled-password --uid 1000 d3ctf --shell /bin/bash
chpasswd <<<"d3ctf:some_random_password"

ssh-keygen -t rsa -q -f "$HOME/.ssh/id_rsa" -N ""
mkdir /home/d3ctf/.ssh && chmod 700 /home/d3ctf/.ssh && chown d3ctf:d3ctf /home/d3ctf/.ssh
cp $HOME/.ssh/id_rsa.pub /home/d3ctf/.ssh/authorized_keys && \
    chmod 600 /home/d3ctf/.ssh/authorized_keys && chown d3ctf:d3ctf /home/d3ctf/.ssh/authorized_keys

# install rootless docker
ssh d3ctf@localhost dockerd-rootless-setuptool.sh install
