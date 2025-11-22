# syntax=docker/dockerfile:1.4

# Stage 1: get the uv binary (faster than pip-installing uv)
FROM ghcr.io/astral-sh/uv:0.2.12 AS uvbuilder

# Stage 2: build the actual application image
FROM python:3.12-slim
# bring in ICU and pkg-config so pyicu can build
RUN apt-get update && \
  apt-get install -y --no-install-recommends curl vim build-essential wget 
# Copy uv binary into the image
COPY --from=uvbuilder /uv /usr/local/bin/uv

# Create virtual environment in /opt/venv
RUN uv venv /opt/venv

# Configure shell to use the virtualenv by default
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only requirements.txt and install dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip install -r requirements.txt

RUN pip freeze > log.txt


# Copy application source code
COPY . /app
WORKDIR /app

# Expose port (if needed) and define entrypoint/command
EXPOSE 8000
CMD ["gunicorn", "os_ams.wsgi:application", "--bind", "0.0.0.0:8000"]
