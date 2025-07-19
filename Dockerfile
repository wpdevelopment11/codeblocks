FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir magika==0.6.1

COPY codeblocks.py /app

ENTRYPOINT ["python3", "codeblocks.py"]
