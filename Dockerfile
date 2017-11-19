FROM            smetj/wishbone:base_python
MAINTAINER      Jelle Smet
RUN             /opt/python/bin/pip3 install --process-dependency-link https://github.com/smetj/wishbone/archive/develop.zip
ENTRYPOINT      ["/opt/python/bin/wishbone"]
