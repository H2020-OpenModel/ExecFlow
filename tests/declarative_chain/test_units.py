from __future__ import annotations

from execflow.calculations.fake import FakeQEPW


def test_qe(generate_declarative_workchain, generate_calcjob_node, samples):
    process = generate_declarative_workchain(samples / "declarative_chain" / "qe_basic.yaml")
    # if we got to this point that means that all validation on schema (which are not complete) was successful
    process.setup()
    assert len(process.ctx.steps) == 1

    # TODO: Don't depend on aiida-qe

    cjob, inputs = process.next_step()

    assert cjob == FakeQEPW

    # test that InputData is put in the right DataNodes and contains the right data
    assert inputs["code"] is None
    from aiida.orm import Dict, KpointsData, StructureData

    assert isinstance(inputs["parameters"], Dict)
    assert isinstance(inputs["kpoints"], KpointsData)
    assert isinstance(inputs["structure"], StructureData)

    assert inputs["parameters"]["CONTROL"]["calculation"] == "scf"
    assert inputs["kpoints"].base.attributes.all["mesh"] == [4, 4, 4]

    node = generate_calcjob_node("quantumespresso.pw")
    process.ctx.current = node.store()
    # we reuse the input parameters as test output
    from aiida.common import LinkType
    from plumpy.process_states import ProcessState

    inputs["parameters"].base.links.add_incoming(
        process.ctx.current, link_type=LinkType.CREATE, link_label="parameters"
    )
    inputs["parameters"].store()
    #
    process.ctx.current.set_process_state(ProcessState.FINISHED)
    process.ctx.current.set_exit_status(0)
    assert process.ctx.current.is_finished_ok

    process.process_current()
    assert process.ctx.current_id == 1
    assert not process.not_finished()

    assert "parameters" in process.ctx.results
    assert process.ctx.results["parameters"] == inputs["parameters"]


# TODO: while if syntax test
# TODO: user type define test
