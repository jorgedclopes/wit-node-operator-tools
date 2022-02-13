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

#### 2) Change directory to the wit_tranfer folder populate the 'list_of_wallets.txt' file.
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
 
#### 3) Run the script
~~~
python3 wit_transfer.py __node_address__ __amount__
~~~
For example
~~~
python3 wit_transfer.py witnet-node-1 200
~~~