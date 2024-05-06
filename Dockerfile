FROM aiidalab/base-with-services:latest

USER ${NB_USER}
WORKDIR "/home/${NB_USER}"

RUN python3 -m venv ${HOME}/openmodel \
    && source ${HOME}/openmodel/bin/activate \
    && pip install --upgrade pip setuptools wheel \
    && pip install ipykernel git+https://github.com/H2020-OpenModel/ExecFlow.git@cwa/fix-26-support-aiida-v24 \
    && python -m ipykernel install --user --name=openmodel --display-name="OpenModel ExecFlow"
