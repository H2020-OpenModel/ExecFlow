FROM aiidalab/base-with-services:latest

USER root

# Make sure pysftp is installed (must be built from source and is a requirement for OTEAPI Core)
RUN mamba install --yes pysftp \
    && mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}"

USER ${NB_USER}
WORKDIR "/home/${NB_USER}"

# Mounts the Execflow package from the local context (directory)
# Including all necessary files for the package to be installed (LICENSE, README.md, pyproject.toml)
RUN --mount=type=bind,source=pyproject.toml,target=/home/${NB_USER}/.cache/execflow/pyproject.toml \
    --mount=type=bind,source=LICENSE,target=/home/${NB_USER}/.cache/execflow/LICENSE \
    --mount=type=bind,source=README.md,target=/home/${NB_USER}/.cache/execflow/README.md \
    --mount=type=bind,source=execflow,target=/home/${NB_USER}/.cache/execflow/execflow \
    pip install ipykernel /home/${NB_USER}/.cache/execflow

# Sets up a custom kernel for the ExecFlow package in Jupyter
RUN python -m ipykernel install --user --name=openmodel --display-name="OpenModel ExecFlow"
