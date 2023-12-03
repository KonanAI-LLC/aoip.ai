#!/bin/bash

# Function to convert bytes to human-readable format
function get_size {
    local -i bytes=$1
    if (( bytes < 1024 )); then
        echo "${bytes}B"
    else
        echo $bytes | awk 'function human(x) {s="B"; if (x>=1024){x/=1024; s="KiB"} if (x>=1024){x/=1024; s="MiB"} if (x>=1024){x/=1024; s="GiB"} if (x>=1024){x/=1024; s="TiB"} return x s} {print human($1)}'
    fi
}

# System Information
echo "========= System Information ========="
uname -a

# Boot Time
echo "=========== Boot Time ============"
uptime -s

# CPU Info
echo "=========== CPU Info ============"
echo "Physical cores: $(lscpu | grep '^CPU(s):' | awk '{print $2}')"
echo "Total cores: $(nproc --all)"
# CPU frequencies
echo "Max Frequency: $(lscpu | grep 'CPU max MHz:' | awk '{print $4}') MHz"
echo "Min Frequency: $(lscpu | grep 'CPU min MHz:' | awk '{print $4}') MHz"
echo "Current Frequency: $(lscpu | grep '^CPU MHz:' | awk '{print $3}') MHz"
# CPU usage
echo "CPU Usage: $(top -b -n1 | grep 'Cpu(s)' | awk '{print $2}')%"

# Memory Information
echo "========= Memory Information ========="
free -h

# Disk Information
echo "========= Disk Information ========="
df -h

# Network Information
echo "========= Network Information ========="
ip addr
