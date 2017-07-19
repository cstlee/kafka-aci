#!/usr/bin/env bash

# Install rkt
echo "Downloading rkt"
pushd /tmp/
wget -q https://github.com/rkt/rkt/releases/download/v1.27.0/rkt_1.27.0-1_amd64.deb
sudo dpkg -i rkt_1.27.0-1_amd64.deb
rm rkt_1.27.0-1_amd64.deb
popd
echo "Finished installing rkt"

# Install acbuild
echo "Downloading acbuild"
pushd /tmp/
wget -q https://github.com/containers/build/releases/download/v0.4.0/acbuild-v0.4.0.tar.gz
tar -xzf acbuild-v0.4.0.tar.gz -C /usr/local/bin/ --strip-components=1
rm acbuild-v0.4.0.tar.gz
popd
echo "Finished installing acbuild"
