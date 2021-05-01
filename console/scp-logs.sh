#!/bin/bash
SRC=192.168.86.244
RSA=~/.ssh/chia-id_rsa
USER=chia

for LOG in $(ssh -i $RSA $USER@$SRC "ls /home/chia/chialogs")
do
  if [ ! -f ../test-logs/$LOG ]
  then
    scp -i $RSA $USER@$SRC:/home/chia/chialogs/$LOG ../test-logs/
  fi
done
