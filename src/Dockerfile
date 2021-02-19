FROM python:3.7 as base
WORKDIR /install

COPY . .
RUN make dev-env
RUN make deps
CMD ["make", "run"]
