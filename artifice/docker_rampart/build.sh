#!/bin/bash
#set -euo pipefail

# Build the compile stage:
docker build --target compile-image \
       --build-arg BUILDKIT_INLINE_CACHE=1 \
       --cache-from=artifice_polio_rampart:compile-stage \
       --tag artifice_polio_rampart:compile-stage .

# Build the runtime stage, using cached compile stage:
docker build --target runtime-image \
       --build-arg BUILDKIT_INLINE_CACHE=1 \
       --cache-from=artifice_polio_rampart:compile-stage \
       --cache-from=artifice_polio_rampart:latest \
       --tag artifice_polio_rampart:latest .

# Push the new versions:
#docker push itamarst/helloworld:compile-stage
#docker push itamarst/helloworld:latest
