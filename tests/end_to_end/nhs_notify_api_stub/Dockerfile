# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install dotenv flask jsonschema requests

COPY --from=root_dir /src/notify/app/utils/ /app/utils/
COPY --from=root_dir /src/notify/app/validators/schemas/nhs-notify.json /app/schema.json
COPY --from=root_dir .env.compose /app/.env
COPY . /app

ENTRYPOINT ["python3"]
CMD ["app.py"]

FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF

# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
