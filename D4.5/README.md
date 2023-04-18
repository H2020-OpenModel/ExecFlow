# How to install
`pip install -e ./ --user`
`aiida-pseudo install sssp`

Install and register a QuantumEspresso pw.x code see [aiida-quantumespresso docs](https://aiida-quantumespresso.readthedocs.io/en/latest/installation/index.html).

# How to run
Change all the paths in the .yaml files to those that make sense, and change the `code` everywhere to the QE code you just installed.
Then it's simply:

`python run_workflow.py <workflow.yaml>`
