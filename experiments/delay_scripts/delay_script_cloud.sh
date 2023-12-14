# DEV=name of the interface
# IP1=Edge1 IP1
# Sets delay from Cloud to Edge1 at 40ms
DEV=enp1s0
IP1=192.168.122.101

if tc qdisc show dev $DEV | grep "qdisc htb 1: root"; then
   tc qdisc del dev $DEV root
fi
tc qdisc add dev $DEV handle 1: root htb

# Sets delay from Cloud to Edge1
tc class add dev $DEV parent 1: classid 1:15 htb rate 100000Mbps
tc qdisc add dev $DEV parent 1:15 handle 11 netem delay 100ms 1ms # this is with normal distribution by default
#tc qdisc add dev $DEV parent 1:15 handle 11 netem delay 60ms 1ms distribution normal #FIXME distribution normal scatena kernel panic
tc filter add dev $DEV parent 1:0 prio 1 protocol ip handle 11 fw flowid 1:15
iptables -A OUTPUT -t mangle -d "$IP1" -j MARK --set-mark 11


