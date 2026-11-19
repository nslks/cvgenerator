# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS build
WORKDIR /src
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv build --wheel --out-dir /dist \
 && uv export --no-dev --no-emit-project --no-hashes --format requirements-txt -o /dist/requirements.txt

FROM debian:trixie-slim

# texlive-xetex: xelatex + fontspec  | latex-recommended: geometry, hyperref, xcolor, microtype
# latex-extra: enumitem, titlesec,     | fonts-recommended: Latin Modern
#   paracol, eso-pic, xltabular        | pictures: tikz/pgf for the skill bars
# lang-german: hyphenation patterns    | fonts-texgyre, fonts-inter + fontconfig: resolve fonts by name
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
        latexmk \
        texlive-xetex \
        texlive-latex-recommended \
        texlive-latex-extra \
        texlive-fonts-recommended \
        texlive-pictures \
        texlive-lang-german \
        fonts-texgyre \
        fonts-inter \
        fontconfig \
 && fc-cache -f \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /dist/ /tmp/dist/
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir -r /tmp/dist/requirements.txt \
 && /opt/venv/bin/pip install --no-cache-dir --no-deps /tmp/dist/*.whl \
 && rm -rf /tmp/dist

COPY templates /opt/cvgenerator/templates

# HOME/TEXMFVAR/XDG_CACHE_HOME under /tmp so the image also runs as an arbitrary
# --user, which is how the host keeps ownership of the generated files.
ENV PATH=/opt/venv/bin:$PATH \
    CVGENERATOR_TEMPLATES=/opt/cvgenerator/templates \
    HOME=/tmp \
    TEXMFVAR=/tmp/texmf-var \
    XDG_CACHE_HOME=/tmp/cache

WORKDIR /work
ENTRYPOINT ["cvgenerator"]
CMD ["build"]
