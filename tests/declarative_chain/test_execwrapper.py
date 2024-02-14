from aiida import orm
from aiida import engine
from execflow.workchains.declarative_chain import DeclarativeChain
import sys

def test_execwrapper(samples):
    from aiida.orm import InstalledCode, load_computer
    res = engine.run(DeclarativeChain, **{
        'workchain_specification': orm.Str(samples / "exec_wrapper.yaml")
    })
    print(res)

    assert res['results']["stdout"].get_content()[0] == '7'
    
