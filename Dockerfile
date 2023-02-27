FROM python:3-alpine

RUN apk add \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    libffi-dev

WORKDIR /home/dirsearch_user
RUN addgroup -S dirsearch_group && adduser -S -G dirsearch_group -s /bin/false dirsearch_user
RUN chmod 2777 /mnt/

ADD . /home/dirsearch_user/dirsearch
RUN chown -R dirsearch_user:dirsearch_group /home/dirsearch_user

USER dirsearch_user
RUN python3 -m pip install --no-cache-dir -r ./dirsearch/requirements.txt

ENTRYPOINT ["/usr/local/bin/python3","/home/dirsearch_user/dirsearch/dirsearch.py"]
CMD ["--help"]