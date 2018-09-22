#!/bin/ash

echo ""
echo ""
echo ""
echo "Welcome to a CoinGame!"
echo "More info at https://github.com/TeskaLabs/coingame"
echo ""
echo ""
echo ""

RABBITMQ_NODENAME="coingamesvrmq"
export RABBITMQ_NODENAME

RABBITMQ_PWD=$(cat /etc/coingamesvr-rabbitmq.passwd)
export RABBITMQ_PWD

/opt/rabbitmq_server/sbin/rabbitmq-server -detached
sleep 5

/opt/rabbitmq_server/sbin/rabbitmqctl delete_user guest
/opt/rabbitmq_server/sbin/rabbitmqctl add_user coingamesvr ${RABBITMQ_PWD}
/opt/rabbitmq_server/sbin/rabbitmqctl set_permissions -p / coingamesvr "" "amq.topic" ""

echo ""
echo "Starting ..."

(cd /opt/coingame && /usr/bin/python3.6 coingamesvr.py -c /opt/coingame/etc/coingamesvr.conf)
