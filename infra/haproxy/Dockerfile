FROM alpine:3.19

RUN apk add --no-cache haproxy keepalived

COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
COPY keepalived.conf /etc/keepalived/keepalived.conf
COPY check_haproxy.sh /usr/local/bin/check_haproxy.sh
RUN chmod +x /usr/local/bin/check_haproxy.sh

EXPOSE 80

CMD sh -c "keepalived -D -f /etc/keepalived/keepalived.conf && haproxy -f /usr/local/etc/haproxy/haproxy.cfg"