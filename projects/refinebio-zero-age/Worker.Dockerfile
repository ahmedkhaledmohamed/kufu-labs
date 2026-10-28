# Built after the hash-checked upstream Dockerfile.base at the pinned source.
FROM kufu/refinebio-base:7b809b7
USER root
ARG FIXTURE_UID=1000
RUN test "$FIXTURE_UID" -ne 0 && usermod --uid "$FIXTURE_UID" user
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 AWS_EC2_METADATA_DISABLED=true
RUN printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d \
    && chmod +x /usr/sbin/policy-rc.d \
    && apt-get update -qq \
    && apt-get install --no-install-recommends -y postgresql-14 \
    && rm -rf /var/lib/apt/lists/*
COPY workers/data_refinery_workers/processors/requirements.txt /tmp/worker-requirements.txt
COPY common/requirements.txt /tmp/common-requirements.txt
# Follow upstream's worker-then-common dependency installation order. This
# exercises metadata export, not the R/Bioconductor expression processing stack.
RUN python3 -m pip install --disable-pip-version-check --no-cache-dir -r /tmp/worker-requirements.txt \
    && python3 -m pip install --disable-pip-version-check --no-cache-dir -r /tmp/common-requirements.txt \
    && python3 -m pip check
USER user
ENTRYPOINT []
