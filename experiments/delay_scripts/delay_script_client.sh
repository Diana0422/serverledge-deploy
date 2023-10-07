# DEV=name of the interface
# IP1=Edge1 IP1
# Sets delay from Client to Edge1 at 5ms
DEV=enp1s0
IP1=192.168.122.2

if tc qdisc show dev $DEV | grep -q "qdisc htb 1: root"; then
    tc qdisc del dev $DEV root
fi
tc qdisc add dev $DEV handle 1: root htb

tc class add dev $DEV parent 1: classid 1:15 htb rate 100000Mbps
tc qdisc add dev $DEV parent 1:15 handle 11 netem delay 5ms 1ms distribution normal
tc filter add dev $DEV parent 1:0 prio 1 protocol ip handle 11 fw flowid 1:15
iptables -A OUTPUT -t mangle -d "$IP1" -j MARK --set-mark 11


