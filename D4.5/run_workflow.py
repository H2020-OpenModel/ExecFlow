import aiida
aiida.load_profile()
from aiida import orm
from aiida import engine
from execflow.workchains.declarative_chain import DeclarativeChain
import sys
import os

if __name__ == "__main__":
    workflow = sys.argv[1]
    all = {
        'workchain_specification': orm.Str(os.path.abspath(workflow))
    }

    engine.run(DeclarativeChain, **all)

