import aiida

aiida.load_profile()
import os
import sys

from aiida import engine, orm
from aiida_tools.workflows.declarative_chain import DeclarativeChain

if __name__ == "__main__":
    workflow = sys.argv[1]
    all = {"workchain_specification": orm.SinglefileData(os.path.abspath(workflow))}

    engine.run(DeclarativeChain, **all)
