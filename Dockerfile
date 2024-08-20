FROM python:3.10

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
   --mount=type=bind,source=requirements.txt,target=requirements.txt \
   python -m pip install -r requirements.txt

COPY ./app .

CMD ["python3", "main.py"] 
