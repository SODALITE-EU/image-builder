FROM openjdk:11.0.8-jre-buster as app-builder
WORKDIR /build/
COPY . /build/
RUN /build/generate.sh


FROM python:3.8.12-alpine3.13 as python-builder
COPY requirements.txt .
RUN export BUILD_PREREQS="gcc musl-dev libffi-dev openssl-dev postgresql-dev cargo" \
    && apk add --no-cache $BUILD_PREREQS \
    && pip3 install --no-cache-dir wheel \
    && pip3 install --user --no-warn-script-location -r requirements.txt


FROM python:3.8.12-alpine3.13

# install system-packages
RUN export PACKAGES="git bash tar openssh-client libpq" \
    && apk add --no-cache $PACKAGES

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
