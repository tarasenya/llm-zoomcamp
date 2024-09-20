FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install pipenv
RUN pip install --upgrade pip
RUN pip install pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
# Install project dependencies
RUN pipenv install --system --deploy

CMD ["streamlit", "run", "app.py", "--server.runOnSave=true"]
