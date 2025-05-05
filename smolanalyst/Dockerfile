FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir numpy pandas matplotlib openpyxl smolagents smolagents[litellm]

RUN mkdir /datasources
RUN mkdir /smolanalyst

WORKDIR /smolanalyst

COPY config.py /app/config.py
COPY prompt.py /app/prompt.py
COPY runner.py /app/runner.py

ENTRYPOINT ["python", "/app/runner.py"]