#!/bin/bash
set -e

BUILD_DIR=$(mktemp -d)

cp haproxy/Dockerfile $BUILD_DIR/
cp haproxy/haproxy.cfg $BUILD_DIR/
cp keepalived/keepalived.conf $BUILD_DIR/
cp keepalived/check_haproxy.sh $BUILD_DIR/

docker build -t haproxy-keepalived $BUILD_DIR
rm -rf $BUILD_DIR

docker run -d --name haproxy-keepalived --net host --cap-add NET_ADMIN --cap-add NET_RAW \
  haproxy-keepalived