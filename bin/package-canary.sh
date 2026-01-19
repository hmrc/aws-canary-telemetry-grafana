#!/bin/bash

### WARNING! This is a generated file and should ONLY be edited in https://github.com/hmrc/telemetry-canary-resources

set -eu

apt install -y zip
mkdir -p build
cd "./${VENV_NAME}/lib/python3.14/site-packages"
zip -r "../../../../build/${CANARY_ZIP_NAME}" .
cd -
cd "./src"
zip -r --grow "../build/${CANARY_ZIP_NAME}" .
cd -
