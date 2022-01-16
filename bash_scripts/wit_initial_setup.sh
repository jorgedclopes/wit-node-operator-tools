#!/bin/bash

sudo apt -y install bc
sudo apt -y install docker.io

docker run -d --name witnet-node-1 --volume ~/.witnet-1:/.witnet --publish 21337:21337 --restart always witnet/witnet-rust
docker run -d --name witnet-node-2 --volume ~/.witnet-2:/.witnet --publish 22337:21337 --restart always witnet/witnet-rust
docker run -d --name witnet-node-3 --volume ~/.witnet-3:/.witnet --publish 23337:21337 --restart always witnet/witnet-rust
docker run -d --name witnet-node-4 --volume ~/.witnet-4:/.witnet --publish 24337:21337 --restart always witnet/witnet-rust
docker run -d --name witnet-node-5 --volume ~/.witnet-5:/.witnet --publish 25337:21337 --restart always witnet/witnet-rust
docker run -d --name witnet-node-6 --volume ~/.witnet-6:/.witnet --publish 26337:21337 --restart always witnet/witnet-rust
docker run -d --name witnet-node-7 --volume ~/.witnet-7:/.witnet --publish 27337:21337 --restart always witnet/witnet-rust
docker run -d --name witnet-node-8 --volume ~/.witnet-8:/.witnet --publish 28337:21337 --restart always witnet/witnet-rust

