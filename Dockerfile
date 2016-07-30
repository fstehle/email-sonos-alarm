FROM python:2.7-alpine

RUN apk add --update \
    build-base \
  && rm -rf /var/cache/apk/*

COPY requirements.txt /app/requirements.txt
RUN pip install -q -r /app/requirements.txt

ADD *.py /app/

ENV PORT 80
EXPOSE 80
ENTRYPOINT ["/app/main.py"]
CMD ["--"]
