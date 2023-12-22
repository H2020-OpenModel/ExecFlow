import sys

from aiida import engine, orm

from execflow.workchains.declarative_chain import DeclarativeChain


def test_simple_execution(samples, fixture_localhost):
    from aiida.orm import InstalledCode, load_computer

    code = InstalledCode(
        label="bash", computer=fixture_localhost, filepath_executable="/bin/bash"
    ).store()
    res = engine.run(
        DeclarativeChain,
        **{
            "workchain_specification": orm.SinglefileData(
                samples / "declarative_chain" / "double_sum.yaml"
            )
        }
    )

    assert res["results"]["sum_1"] == 9
    assert res["results"]["sum_2"] == 14
