def test_list(generate_declarative_workchain, generate_calcjob_node, samples):
    process = generate_declarative_workchain(samples / "declarative_chain" / "list.yaml")
    process.setup()
    cjob, inputs = process.next_step()
    print(inputs)
    assert inputs["x"][0] == 3
    assert inputs["x"][1] == 3