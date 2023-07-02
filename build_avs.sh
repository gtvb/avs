#!/usr/bin/env bash
set -e

[ "$#" -ge 2 ] || { echo "Usage: $0 <image> [<tag>]" >&2; exit 1; }

readonly IMAGE="${1}"
readonly FINAL_TAG="${2:-latest}"
readonly CONTEXT_DIR="$(cd "$(dirname "${0}")" && pwd)"

# Use buildkit to enable --cache-from support
export DOCKER_BUILDKIT=1

# Build build-stage so that it can be used as a source of cached layers in subsequent builds
docker build \
  --target build-stage \
  --cache-from "${IMAGE}:build-stage" \
  --tag "${IMAGE}:build-stage" \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  "${CONTEXT_DIR}"
  
# Build the final image
docker build \
  --cache-from "${IMAGE}:build-stage" \
  --cache-from "${IMAGE}:latest" \
  --tag "${IMAGE}:latest" \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  "${CONTEXT_DIR}"
  
# # Push the final image
# docker tag "${IMAGE}:latest" "${IMAGE}:${FINAL_TAG}"
# docker push "${IMAGE}:${FINAL_TAG}"

# # Push images to serve as cache sources for future builds
# docker push "${IMAGE}:build-stage"
# docker push "${IMAGE}:latest"
