FROM            smetj/wishbone:base_python
ARG             branch
MAINTAINER      Jelle Smet
RUN             LC_ALL=en_US.UTF-8 /opt/python/bin/pip3 install --process-dependency-link https://github.com/smetj/wishbone/archive/$branch.zip
ENTRYPOINT      ["/opt/python/bin/wishbone"]
