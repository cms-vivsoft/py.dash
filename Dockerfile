FROM python:3.8.7

RUN python3 -m pip install gunicorn


# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /cms_dash

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY ./cms_dash .

CMD ["gunicorn", "index:server", "-b", ":8050", "--timeout", "90", "--worker-class", "sync"]
