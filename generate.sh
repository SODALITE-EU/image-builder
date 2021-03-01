#!/bin/sh

set -e
set -u

[ -f openapi-generator-cli-4.3.0.jar ] || wget https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/4.3.0/openapi-generator-cli-4.3.0.jar
rm -rf gen/
rm -rf src/image_builder/api/openapi/
java -jar openapi-generator-cli-4.3.0.jar generate \
    --input-spec openapi-spec.yml \
    --api-package api \
    --invoker-package invoker \
    --model-package models \
    --generator-name python-flask \
    --strict-spec true \
    --output gen/ \
    --config openapi-python-config.yml
cp -r gen/image_builder/api/openapi/ src/image_builder/api/
rm -rf src/image_builder/api/openapi/test/
rm -rf src/image_builder/api/openapi/CONTROLLER_PACKAGE_MATCH_ANCHOR/
rm src/image_builder/api/openapi/__main__.py
sed -i -E -e 's/(.*?) .*?CONTROLLER_PACKAGE_MATCH_ANCHOR*/\1 image_builder.api.controllers/g' src/image_builder/api/openapi/openapi/openapi.yaml
