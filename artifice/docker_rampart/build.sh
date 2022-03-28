#!/bin/bash
#set -euo pipefail

# Build the compile stage:
docker build --target compile-image \
       --build-arg BUILDKIT_INLINE_CACHE=1 \
       --cache-from=coreyansley/artifice_polio_rampart:compile-stage \
       --tag coreyansley/artifice_polio_rampart:compile-stage .

# Build the runtime stage, using cached compile stage:
docker build --target runtime-image \
       --build-arg BUILDKIT_INLINE_CACHE=1 \
       --cache-from=coreyansley/artifice_polio_rampart:compile-stage \
       --cache-from=coreyansley/artifice_polio_rampart:latest \
       --tag coreyansley/artifice_polio_rampart:latest .

# Push the new versions:
#docker push itamarst/helloworld:compile-stage
#docker push itamarst/helloworld:latest
