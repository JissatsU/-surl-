#!/bin/bash

iptables -D INPUT -s $1 -i $2 -p tcp -m tcp -j DROP
