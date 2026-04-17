FROM mambaorg/micromamba:2.0.5

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml

RUN micromamba install -y -n base -f /tmp/environment.yml && \
    micromamba clean --all --yes

# Ensure jupyter/nbconvert are in base even if not in environment.yml
RUN micromamba install -y -n base -c conda-forge \
      jupyter nbconvert ipykernel && \
    micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1
ENV PATH=/opt/conda/bin:$PATH

WORKDIR /work

CMD ["bash"]