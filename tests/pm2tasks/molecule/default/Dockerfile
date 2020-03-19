FROM docker.io/pycontribs/centos:8

# Current pm2 requires node >= 8.10.0
RUN yum update -y && yum install -y nodejs
RUN npm install -g pm2
