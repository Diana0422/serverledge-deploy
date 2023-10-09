# DEV=name of the interface
# IP1=Edge2 IP1
# IP2=Edge3 IP2
# IP3=Cloud IP3
DEV=enp1s0
IP1=192.168.122.4
IP2=192.168.122.5
IP3=192.168.122.6

if tc qdisc show dev $DEV | grep -q "qdisc htb 1: root"; then
    tc qdisc del dev $DEV root
fi
tc qdisc add dev $DEV handle 1: root htb

# Sets delay from Edge1 to Edge2 at 1ms
tc class add dev $DEV parent 1: classid 1:15 htb rate 100000Mbps
tc qdisc add dev $DEV parent 1:15 handle 11 netem delay 1ms 1ms distribution normal
tc filter add dev $DEV parent 1:0 prio 1 protocol ip handle 11 fw flowid 1:15
iptables -A OUTPUT -t mangle -d "$IP1" -j MARK --set-mark 11

# Nota: class_id 16 e handle 12
# Sets delay from Edge1 to Edge3 at 1ms
tc class add dev $DEV parent 1: classid 1:16 htb rate 100000Mbps
tc qdisc add dev $DEV parent 1:16 handle 12 netem delay 1ms 1ms distribution normal
tc filter add dev $DEV parent 1:0 prio 1 protocol ip handle 12 fw flowid 1:16
iptables -A OUTPUT -t mangle -d "$IP2" -j MARK --set-mark 12

# Nota: class_id 17 e handle 13
# Sets delay from Edge1 to Cloud at 40ms
tc class add dev $DEV parent 1: classid 1:17 htb rate 100000Mbps
tc qdisc add dev $DEV parent 1:17 handle 13 netem delay 40ms 1ms distribution normal
tc filter add dev $DEV parent 1:0 prio 1 protocol ip handle 13 fw flowid 1:17
iptables -A OUTPUT -t mangle -d "$IP3" -j MARK --set-mark 13