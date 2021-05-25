#!/usr/bin/env bash

set -e

if [ "$1" = 'job' ]; then
  exec python3 -m shell_manager.server
fi

exec "$@"