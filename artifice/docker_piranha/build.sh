#!/bin/bash
#set -euo pipefail

# Build the compile stage:
docker build --target compile-image \
       --build-arg BUILDKIT_INLINE_CACHE=1 \
       --cache-from=coreyansley/artifice_piranha:compile-stage \
       --tag coreyansley/artifice_piranha:compile-stage .

# Build the runtime stage, using cached compile stage:
docker build --target runtime-image \
       --build-arg BUILDKIT_INLINE_CACHE=1 \
       --cache-from=coreyansley/artifice_piranha:compile-stage \
       --cache-from=coreyansley/artifice_piranha:latest \
       --tag coreyansley/artifice_piranha:latest .

# Push the new versions:
#docker push itamarst/helloworld:compile-stage
#docker push itamarst/helloworld:latest
