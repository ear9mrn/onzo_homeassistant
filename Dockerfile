ARG BUILD_FROM
FROM $BUILD_FROM
RUN \
  apk add --no-cache \
    python3 py3-pip py3-hidapi py3-requests

COPY . /
RUN chmod 755 /run.sh
CMD ["/run.sh"]

