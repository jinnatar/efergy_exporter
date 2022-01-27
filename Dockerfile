FROM python:3.10 AS poetry_builder
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python -

FROM poetry_builder as builder
RUN mkdir /build
WORKDIR /build
COPY efergy_exporter ./efergy_exporter
COPY poetry.lock pyproject.toml ./
RUN poetry build -f wheel

# Temporary image pending PR to upstream
FROM hertzg/rtl_433:debian
RUN apt update && apt install -y --no-install-recommends python3-pip
WORKDIR /srv
COPY --from=builder /build/dist/*.whl ./
RUN pip3 install *.whl

ENTRYPOINT ["efergy_exporter"]
