#!/bin/bash

########################################################################################
#
# This script takes the destination wallet address and sends the excedent witnet tokens
# to that wallet - alternative to mint address/percentage configuration
#
# EXAMPLE - HOW TO RUN
# ./wittransfer.sh WALLET_ADDRESS
#
########################################################################################

WALLET_ADDRESS=$1
NODE_COUNT=8

for ((ii=1;ii<=$NODE_COUNT;ii++));
do
        END_AMOUNT=300
        THRESHOLD=500
        CONTAINER_NAME=witnet-node-$ii
        BALANCE_FULL_OUTPUT=$(sudo docker exec $CONTAINER_NAME witnet node balance)
        WITNET_AMOUNT=$(echo $BALANCE_FULL_OUTPUT | cut -d ' ' -f 14) # 250.000000000
        echo "Currency Amount: "$WITNET_AMOUNT
        if (( $(echo $WITNET_AMOUNT-$THRESHOLD'>'0 | bc -l) )); then
                TRANSFER_AMOUNT=$(echo "$WITNET_AMOUNT-$END_AMOUNT" | bc -l)
                TRANSFER_AMOUNT_NANOWIT_FLOAT=$(echo "$TRANSFER_AMOUNT*10^9" | bc -l)
                TRANSFER_AMOUNT_NANOWIT=${TRANSFER_AMOUNT_NANOWIT_FLOAT%.*}
                echo "Amount transfered (nanoWit): "$TRANSFER_AMOUNT_NANOWIT
                # transfer
                echo $CONTAINER_NAME "is sending " $TRANSFER_AMOUNT_NANOWIT "to" $WALLET_ADDRESS
                sudo docker exec $CONTAINER_NAME witnet node send --address=$WALLET_ADDRESS --value=$TRANSFER_AMOUNT_NANOWIT --fee=1
        fi
done
