FROM openjdk:11.0.8-jre-buster as app-builder
WORKDIR /build/
COPY . /build/
RUN /build/generate.sh


FROM python:3.8.8-alpine3.13 as python-builder
COPY requirements.txt .
RUN export BUILD_PREREQS="gcc musl-dev libffi-dev openssl-dev postgresql-dev cargo" \
    && apk add --no-cache $BUILD_PREREQS \
    && pip3 install --no-cache-dir wheel \
    && pip3 install --user --no-warn-script-location -r requirements.txt

FROM alpine:3.13 AS docker-buildx
ARG TARGETPLATFORM
ARG BUILDX_VERSION=0.5.1
RUN BUILDX_ARCH=$(case ${TARGETPLATFORM:-linux/amd64} in \
    "linux/amd64")   echo "amd64"   ;; \
    "linux/arm/v7")  echo "arm-v7"  ;; \
    "linux/arm64")   echo "arm64"   ;; \
    *)               echo ""        ;; esac) \
  && echo "BUILDX_ARCH=$BUILDX_ARCH" \
  && mkdir -p /opt \
  && set -x; wget -q "https://github.com/docker/buildx/releases/download/v${BUILDX_VERSION}/buildx-v${BUILDX_VERSION}.linux-${BUILDX_ARCH}" -qO "/opt/docker-buildx" \
  && chmod +x /opt/docker-buildx


FROM python:3.8.8-alpine3.13

# install system-packages
RUN export PACKAGES="git bash tar openssh-client libpq docker" \
    && apk add --no-cache $PACKAGES

# copy buildx binaries
COPY --from=docker-buildx /opt/docker-buildx /usr/libexec/docker/cli-plugins/docker-buildx

# copy python packages
COPY --from=python-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# install ansible roles and collections
COPY requirements.yml .
RUN ansible-galaxy install -r requirements.yml \
    && rm requirements.yml

# copy app code
COPY --from=app-builder /build/src/ /app/
COPY openapi-spec.yml /app/

WORKDIR /app
ENTRYPOINT ["python3"]
CMD ["-m", "image_builder.api.cli"]
