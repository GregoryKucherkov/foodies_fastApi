FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

# Set working directory
WORKDIR $APP_HOME

# Install Poetry
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry && \
    rm -rf /var/lib/apt/lists/*


# Copy dependency files first
COPY pyproject.toml poetry.lock ./

# Install dependencies (without virtualenv)
RUN poetry config virtualenvs.create false && \
    poetry install --only main


COPY ./volumes/foodies-api/static/ ./public/

# Copy the rest of the project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]