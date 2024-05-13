FROM aiidalab/base-with-services:latest

USER ${NB_USER}
WORKDIR "/home/${NB_USER}"

RUN python -m pip install --upgrade pip && \
    pip install --upgrade setuptools wheel && \
    pip install ipykernel git+https://github.com/H2020-OpenModel/ExecFlow.git && \
    python -m ipykernel install --user --name=openmodel --display-name="OpenModel ExecFlow"
