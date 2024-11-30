FROM scottyhardy/docker-wine:latest
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y --no-install-recommends \
    python3.8 python3.8-distutils python3-pip && \
    ln -s /usr/bin/python3.8 /usr/bin/python && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY /python_server/main.py /app/app.py
COPY /python_server/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt


RUN mkdir files output
COPY code_smaller.zip /app/files
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
ENTRYPOINT ["/start.sh"]