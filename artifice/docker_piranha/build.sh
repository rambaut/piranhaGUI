#!/bin/bash
#set -euo pipefail

# Build the compile stage:
docker build --target compile-image \
       --build-arg BUILDKIT_INLINE_CACHE=1 \
       --cache-from=artifice_piranha:compile-stage \
       --tag artifice_piranha:compile-stage .

# Build the runtime stage, using cached compile stage:
docker build --target runtime-image \
       --build-arg BUILDKIT_INLINE_CACHE=1 \
       --cache-from=artifice_piranha:compile-stage \
       --cache-from=artifice_piranha:latest \
       --tag artifice_piranha:latest .

# Push the new versions:
#docker push itamarst/helloworld:compile-stage
#docker push itamarst/helloworld:latest
