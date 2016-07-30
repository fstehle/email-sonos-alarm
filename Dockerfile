FROM python:2.7-alpine

COPY requirements.txt /app/requirements.txt
RUN pip install -q -r /app/requirements.txt

ADD *.py /app/

ENV PORT 80
EXPOSE 80
ENTRYPOINT ["/app/main.py"]
CMD ["--"]