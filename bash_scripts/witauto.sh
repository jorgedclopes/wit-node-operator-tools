#!/bin/bash

########################################################################################
#
# This script takes a set of node config files and
# edits their public address, mint address and percentage
#
# There are some information that needs to be passed to the script for it to do its work
# EXAMPLE - HOW TO RUN
# ./witauto.sh IPv4_ADDRESS WALLET_ADDRESS
#
########################################################################################

IP=$1
WALLET_ADDRESS=$2
BASE_PORT=20337
DELTA=1000
NODE_COUNT=8
# this DELTA/NODE_COUNT combination works for at most 10 nodes.

for ((ii=1;ii<=$NODECOUNT;ii++));
do
        PORT=$(($BASE_PORT + $DELTA*$ii))

        IP_OLD_PATTERN="public_addr.*"
        IP_NEW_PATTERN='public_addr = "'$IP:$PORT'"'
        FILE=~/.witnet-$ii/config/witnet.toml

	WALLET_OLD_PATTERN="#mint_external_address.*"
        WALLET_NEW_PATTERN='mint_external_address = "'$WALLET_ADDRESS'"'

        PERCENTAGE_OLD_PATTERN="#mint_external_percentage.*"
        PERCENTAGE_NEW_PATTERN='mint_external_percentage = 100'

        #echo $("s/$IP_OLD_PATTERN/$IP_NEW_PATTERN/g" $FILE)
        sed -i "s/$IP_OLD_PATTERN/$IP_NEW_PATTERN/g" $FILE
        sed -i "s/$WALLET_OLD_PATTERN/$WALLET_NEW_PATTERN/g" $FILE
        sed -i "s/$PERCENTAGE_OLD_PATTERN/$PERCENTAGE_NEW_PATTERN/g" $FILE

done
