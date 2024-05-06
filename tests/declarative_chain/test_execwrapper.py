from __future__ import annotations

from aiida import engine, orm

from execflow.workchains.declarative_chain import DeclarativeChain


def test_execwrapper(samples):

    res = engine.run(DeclarativeChain, workchain_specification=orm.Str(samples / "exec_wrapper.yaml"))
    print(res)

    assert res["results"]["stdout"].get_content()[0] == "7"
