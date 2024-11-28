FROM scottyhardy/docker-wine:latest
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y --no-install-recommends \
    unzip && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir files output
COPY code_smaller.zip /app/files
COPY start.sh /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]