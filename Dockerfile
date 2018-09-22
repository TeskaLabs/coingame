FROM alpine:3.8
LABEL maintainer="TeskaLabs Ltd <support@teskalabs.com>"

COPY ./docker/start.sh /start.sh
COPY ./coingamesvr.py /opt/coingame/coingamesvr.py
COPY ./asabcoin /opt/coingame/asabcoin
COPY ./webui /opt/coingame/webui
COPY ./docker/coingamesvr.conf /opt/coingame/etc/coingamesvr.conf

RUN set -x \
	&& apk upgrade --no-cache \
	&& apk add --update --no-cache \
		erlang \
		erlang-sasl \
		erlang-mnesia \
		erlang-ssl \
		erlang-eldap \
		erlang-xmerl \
		erlang-os-mon \
		xz \
		python3 \
		pwgen \
	# Install RabbitMQ
	&& wget https://dl.bintray.com/rabbitmq/all/rabbitmq-server/3.7.7/rabbitmq-server-generic-unix-3.7.7.tar.xz -O - | xz -d | tar x -C /opt/ \
	&& ln -s /opt/rabbitmq_server-3.7.7 /opt/rabbitmq_server \
	&& pwgen 20 1 > /etc/coingamesvr-rabbitmq.passwd \
	# Configure Python
	&& python3 -m ensurepip \
	&& rm -r /usr/lib/python*/ensurepip \
	&& pip3 install --upgrade pip setuptools \
	&& pip3 install --upgrade aiohttp pika pyyaml asab \
	# Finalize
	&& chmod a+x /start.sh

WORKDIR /
CMD ["/start.sh"]

EXPOSE 80/tcp
EXPOSE 5672/tcp
