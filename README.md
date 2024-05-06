# ExecFlow

This repo holds all the parts that relate to ExecFlow.

## Declarative Chain

This is a self assembling workchain that utilizes json or yaml files to specify both the steps in the workchain as well as the data to be used with it.

### Syntax

The overall structure of the input files are as follows:

```yaml
---
steps:
- calcjob: <aiida calcjob or calculation entry point>
  inputs:
    <dict with inputs for the calcjob>
```

The array of steps will be ran sequentially inside the workchain. The structure above is the most basic form of a workflow file.

#### Data Referencing

To keep the files clean and readable, it is possible to first specify some data and then reference it in the `steps` part of the workflow file. For example:

```yaml
---
data:
    kpoints:
    - 6
    - 6
    - 6
steps:
- calcjob: quantumespresso.pw
  inputs:
    kpoints:
        "$ref": "#/data/kpoints"
    <other inputs>
```

will paste the definition of `kpoints` in the `data` section into the input where it's referenced. This uses [jsonref](https://pypi.org/project/jsonref/), see its documentation for more possibilities. It is for example also possible to reference data from an external json/yaml file.

#### Jinja templates

Often, we want to use the workchain context `self.ctx` to store and retrieve intermediate results throughout the workchain's execution. To facilitate this we can use [jinja](https://jinja.palletsprojects.com/en/3.1.x/) templates such as:
`"{{ ctx.scf_dir }}"` to resolve certain values into the yaml script. The use of will become clear later.

#### Setup

The top level `setup` statement allows for specifying some templates that will be executed before the main steps of the workchain.
This allows for the definition of context variables, e.g.

```yaml
---
setup:
- "{{ 1 | to_ctx('count') }}"
```

sets the `self.ctx.count` variable to `1`.

#### PostProcessing

By defining a `postprocess` field, common operations can be performed that will run _after_ the execution of the `current` calcjob. For example

```yaml
---
data:
    <data>
steps:
- calcjob: quantumespresso.pw
  inputs:
    <inputs>
  postprocess:
  - "{{ ctx.current.outputs['remote_folder'] | to_ctx('scf_dir') }}"
- calcjob: quantumespresso.pw
  inputs:
    parameters:
        "$ref": "#/data/pw_parameters"
    parameters.CONTROL.calculation: nscf
    parent_folder: "{{ ctx.scf_dir }}"
```

Here we can observe a couple of new constructs. The first is `ctx.current`, signifying the currently executed calcjob (i.e. the `scf` calculation). Secondly, the `|` and `to_ctx` in `"{{ ctx.current.outputs['remote_folder'] | to_ctx('scf_dir') }}"` mean the value is piped through a the `to_ctx` filter, which assigns it to the variable `scf_dir`, stored in the workchain's context `self.ctx` for later referencing. Indeed we see that in the next step we retrieve this value using `"{{ ctx.scf_dir }}"` as the `parent_folder` input. Finally we note the line `parameters.CONTROL.calculation: nscf`, this simply means that we set a particular value in the `parameters` dictionary.

#### If

Steps can define an `if` field which contains a statement. If the statement is true, the step will be executed, otherwise it is ignored.

```yaml
---
steps:
- if: "{{ ctx.should_run }}"
  calcjob: quantumespresso.pw
  inputs:
    <inputs>
```

Here, depending on the previously set `ctx` variable, the step will run.

> **Note** the corresponding else statement would be `"{{ not ctx.should_run }}"`

#### While

It is possible to specify a `while` field, with a sequence of steps that will be run until the while statement is false, e.g.:

```yaml
---
steps:
- while: "{{ ctx.count < 5 }}"
  steps:
    - calcjob: quantumespresso.pw
      inputs:
        <inputs>
      postprocess:
      - "{{ (ctx.count + 1) | to_ctx('count') }}"
```

will run the same calcjob 4 times

> **Note** Don't forget to set the ctx.count variable to something in the setup step of the workchain or the postprocessing step of the previous calcjob.

#### Error

It is possible that one of the steps errors. The error code and message will always be reported by the workchain. It is also possible to explicitely specify an error to return from the workchain if this happens using:

```yaml
---
steps:
- calcjob: quantumespresso.pw
  inputs:
        <inputs>
  error:
    code: 23
    message: "The first pw calculation failed."
```

#### Further examples

For a fully featured example, see the `bands.yaml` file in the examples directory which mimics largely the `PwBandsWorkchain` from the [aiida-quantumespresso](https://github.com/aiidateam/aiida-quantumespresso) package.

## data/cuds.py

An AiiDA plugin that interfaces CUDS with AiiDA DataNodes.
For now, CUDS defined through [dlite](https://github.com/SINTEF/dlite) are supported

**This is experimental, pre-alpha software**.

## Prerequisites

As pre-alpha software, this package is **not** released on PyPI.
Currently the only way to install the plugin is to clone the
repository and use `pip`:

```bash
pip install -e .
```

## Acknowledgements

The `DeclarativeChain` was developed and design with help and input of Simon Adorf (@csadorf).
