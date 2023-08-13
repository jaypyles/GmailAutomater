FROM python:slim
WORKDIR /app
COPY .env pyproject.toml pdm.lock /app
COPY src /app/src
RUN pip install pdm
RUN pdm install
CMD ["pdm", "run", "python", "src/gmailautomater/app.py"]
