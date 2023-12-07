#!/bin/bash

### WARNING! This is a generated file and should ONLY be edited in https://github.com/hmrc/telemetry-canary-resources

set -xeu

# Debug Python environment
python --version
pip --version

# Initialise directories
BASEDIR=/data
cd ${BASEDIR}

# Force Debian to use HTTPS
cp /etc/apt/sources.list /etc/apt/sources.list.bak
sed --in-place 's|http://|https://|g' /etc/apt/sources.list

# Update the package listing, so we know what package exist:
apt-get update

# Install security updates:
apt-get -y upgrade

# Install test requirements
python -m venv "${VENV_NAME}"
source ./"${VENV_NAME}"/bin/activate
export PIP_INDEX_URL=https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple
pip install --upgrade pip
pip install --requirement "${REQUIREMENTS_FILE}"

exec "$@"
