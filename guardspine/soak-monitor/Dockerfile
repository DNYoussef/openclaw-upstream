FROM alpine:3.21

RUN apk add --no-cache curl postgresql-client

COPY health-check.sh /usr/local/bin/health-check.sh
RUN chmod +x /usr/local/bin/health-check.sh

RUN adduser -D -s /bin/sh appuser
USER appuser

CMD ["/usr/local/bin/health-check.sh"]
