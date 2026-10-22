# Clean image for microservice-identification.
# Build (from the repo root):  docker build --platform linux/amd64 -t micro-ident-img .
#
# Python 3.7 is required: the pinned deps have no wheels for newer Pythons, and
# LDA.py uses gensim.models.wrappers, which was removed in gensim 4.

FROM python:3.7-slim-bullseye AS base
# Debian 11 LTS ended on 31 Aug 2026 and its security repo was retired; install from main only
RUN grep -rl bullseye-security /etc/apt/ | xargs -r sed -i '/bullseye-security/d'

# ---- Stage 1: build Mallet ----
# This whole stage (JDK, ant, git, Mallet sources) is thrown away; only /opt/mallet is copied out.
FROM base AS mallet
ENV JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-11-jdk-headless ant git \
    && rm -rf /var/lib/apt/lists/*
# Pinned to v2.0.8: newer Mallet uses Maven instead of Ant.
# After building, keep only what bin/mallet needs at runtime: bin/, class/ and lib/mallet-deps.jar.
# Sources, git history, samples and build files are deleted (28 MB -> about 9 MB).
RUN git clone --depth 1 --branch v2.0.8 https://github.com/mimno/Mallet.git /opt/mallet-src \
    && cd /opt/mallet-src && ant \
    && mkdir -p /opt/mallet/lib \
    && cp -r bin class /opt/mallet/ \
    && cp lib/mallet-deps.jar /opt/mallet/lib/ \
    && cd / && rm -rf /opt/mallet-src

# ---- Stage 2: final image ----
FROM base
ENV JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MPLBACKEND=Agg

# Java 11 runs the parser and Mallet; Maven rebuilds symbolsolver-1.0.jar
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-11-jdk-headless maven \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade "pip<24" "setuptools<60" wheel \
    && pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Settings.py expects Mallet at ~/.mallet/bin/mallet
COPY --from=mallet /opt/mallet /root/.mallet

# Pre-download Maven dependencies so rebuilding the jar is fast
COPY symbolsolver/pom.xml /tmp/symbolsolver/pom.xml
RUN cd /tmp/symbolsolver && (mvn -q -B dependency:go-offline || true) && rm -rf /tmp/symbolsolver

WORKDIR /workspace
CMD ["bash"]
