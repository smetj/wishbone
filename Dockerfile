FROM alpine:latest
MAINTAINER Jelle Smet
ARG branch
RUN apk add --update alpine-sdk python3 python3-dev build-base
RUN LC_ALL=en_US.UTF-8 /usr/bin/pip3 install --process-dependency-link https://github.com/smetj/wishbone/archive/$branch.zip
RUN rm -rf /var/cache/apk/*
EXPOSE 19283
ENTRYPOINT ["/usr/bin/wishbone"]
