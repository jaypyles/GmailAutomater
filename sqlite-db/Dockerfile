FROM debian:stable-slim

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -yq --no-install-recommends install sqlite3=3.* && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    mkdir -p /root/db

WORKDIR /root/db
VOLUME /root/db/
COPY ./sqlite-db/data/gmail.sql /root/db/gmail.sql
RUN sqlite3 gmail.db < /root/db/gmail.sql
ENTRYPOINT ["sqlite3", "/root/db/gmail.db"]
