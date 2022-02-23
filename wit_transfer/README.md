# Witnet Transfer Script

### Statement of Purpose
There is a need to make a big number of transfers
from 1 node to different wallets.

### How to use this
#### 1) Clone this repo
~~~
git clone https://github.com/jorgedclopes/wit-node-operator-tools.git
~~~
This repository has a small collection of projects

#### 2) (Optional) Install python, pip and update dependencies
I'll add details for this step just in case the machine has not been fully setup with python packages and dependencies
and someone less tech savvy wants to use these tool.

In order to install python packages we need to install <em>pip</em> and the packages under requirements.
~~~
sudo apt install python3-pip
sudo pip3 install -r ../requirements.txt
~~~

#### 3) Change directory to the wit_tranfer folder populate the 'list_of_wallets.txt' file.
~~~
cd wit_transfer
nano list_of_wallets.txt
~~~
(You can also use any other editor of your choice)  
Example of content in list_of_wallets.txt:
~~~
twit1ulyzvnknjnndkfva636erkkp83wxhhwdfhpabc
twit1ulyzvnknjnndkfva636erkkp83wxhhwdfhpdef
~~~
The script will read 1 address per line so make sure to keep that format.

(Be aware: The addresses in this example are not real)
 
#### 4) Run the script
~~~
python3 wit_transfer.py __node_address__ __amount__
~~~
For example
~~~
python3 wit_transfer.py witnet-node-1 200
~~~