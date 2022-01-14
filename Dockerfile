FROM openjdk:11.0.8-jre-buster as app-builder
WORKDIR /build/
COPY . /build/
RUN /build/generate.sh

FROM python:3.8.12-alpine3.13 as python-builder
WORKDIR /app
COPY requirements.txt .
RUN export BUILD_PREREQS="gcc musl-dev libffi-dev postgresql-dev openssl-dev cargo" \
    && apk add --no-cache $BUILD_PREREQS \
    && pip3 install --no-cache-dir wheel \
   #  && pip3 install --user --no-warn-script-location -r requirements.txt
    && pip3 wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM alpine:3.11 AS idmap
RUN apk add --no-cache autoconf automake build-base byacc gettext gettext-dev gcc git libcap-dev libtool libxslt
RUN git clone https://github.com/shadow-maint/shadow.git /shadow
WORKDIR /shadow
RUN git checkout 59c2dabb264ef7b3137f5edb52c0b31d5af0cf76
RUN ./autogen.sh --disable-nls --disable-man --without-audit --without-selinux --without-acl --without-attr --without-tcb --without-nscd \
  && make \
  && cp src/newuidmap src/newgidmap /usr/bin

FROM python:3.8.12-alpine3.13

# install system-packages
# TODO try to remove as much as possible of system packages
RUN export PACKAGES="gcc musl-dev libffi-dev postgresql-dev openssl-dev cargo git bash tar openssh-client qemu img" \
    && apk add --no-cache $PACKAGES

# copy python packages
# TODO remove from /home/user, don't want to chown all the python files
WORKDIR /app
COPY --from=python-builder /app/wheels /wheels
COPY --from=python-builder /app/requirements.txt .

# copy app code
COPY --from=app-builder /build/src/ /app/
COPY openapi-spec.yml /app/

COPY --from=idmap /usr/bin/newuidmap /usr/bin/newuidmap
COPY --from=idmap /usr/bin/newgidmap /usr/bin/newgidmap

RUN chmod u+s /usr/bin/newuidmap /usr/bin/newgidmap \
  && adduser -D -u 1000 user \
  && mkdir -p /run/user/1000 \
  && chown -R user /run/user/1000 /home/user /home /tmp /app/ \
  && echo user:100000:65536 | tee /etc/subuid | tee /etc/subgid

USER user
ENV USER user
ENV HOME /home/user
ENV XDG_RUNTIME_DIR=/run/user/1000

# Why is there no swagger-ui?
RUN pip install --no-cache /wheels/*
RUN pip install swagger-ui-bundle
ENV PATH=/home/user/.local/bin:$PATH

# install ansible roles and collections
COPY requirements.yml .
RUN ansible-galaxy install -r requirements.yml

WORKDIR /app
ENTRYPOINT ["python3"]
CMD ["-m", "image_builder.api.cli"]
