"""AiiDA WorkChain for the OTE Pipeline."""
from typing import TYPE_CHECKING

from aiida import orm
from aiida.common.exceptions import InputValidationError, ValidationError
from aiida.engine import run, run_get_node, while_
from aiida.engine.processes.workchains.workchain import WorkChain
from aiida.plugins import CalculationFactory, WorkflowFactory

from execflow.wrapper.data.declarative_pipeline import OTEPipelineData

if TYPE_CHECKING:  # pragma: no cover
    from aiida.engine.processes.workchains.workchain import WorkChainSpec


class OTEPipeline(WorkChain):
    """Run an OTE Pipeline.

    Inputs:
        - **pipeline**
          (:py:class:`~execflow.wrapper.data.declarative_pipeline.OTEPipelineData`,
          :py:class:`aiida.orm.Dict`, :py:class:`aiida.orm.SinglefileData`,
          :py:class:`aiida.orm.Str`) -- The declarative pipeline as an AiiDA-valid
          type. Either as a path to a YAML file or the explicit content of the YAML
          file.
        - **run_pipeline** (:py:class:`aiida.orm.Str`) -- The pipeline to run.
          The pipeline name should match a pipeline given in the declarative pipeline
          given in the `pipeline` input.

    Outputs:
        - **session** (:py:class:`aiida.orm.Dict`) -- The OTE session object after
          running the pipeline.

    Outline:
        - :py:meth:`~execflow.wrapper.workflows.pipeline.OTEPipeline.setup`
        - while
          :py:meth:`~execflow.wrapper.workflows.pipeline.OTEPipeline.not_finished`:

          - :py:meth:`~execflow.wrapper.workflows.pipeline.OTEPipeline.submit_next`
          - :py:meth:`~execflow.wrapper.workflows.pipeline.OTEPipeline.process_current`

        - :py:meth:`~execflow.wrapper.workflows.pipeline.OTEPipeline.finalize`

    Exit Codes:
        - **2** (*ERROR_SUBPROCESS*) -- A subprocess has failed.

    """

    @classmethod
    def define(cls, spec: "WorkChainSpec") -> None:
        super().define(spec)

        # Inputs
        spec.input(
            "pipeline",
            valid_type=(OTEPipelineData, orm.Dict, orm.SinglefileData, orm.Str),
            required=True,
        )
        spec.input("run_pipeline", valid_type=orm.Str, required=False)

        # Outputs
        spec.output("session", valid_type=orm.Dict)

        # Outline
        spec.outline(
            cls.parse_pipeline,
            cls.setup,
            while_(cls.not_finished)(cls.submit_next, cls.process_current),
            cls.finalize,
        )

        # Exit Codes
        spec.exit_code(2, "ERROR_SUBPROCESS", message="A subprocess has failed.")

    def parse_pipeline(self) -> None:
        """Parse the pipeline input."""
        result = run(
            CalculationFactory("execflow.parse_pipeline"),
            pipeline_input=self.inputs.pipeline,
        )
        self.ctx.pipeline = result["result"]
        self.ctx.strategy_configs = result["strategy_configs"]

    def setup(self) -> None:  # pylint: disable=too-many-branches
        """Setup WorkChain

        Steps:

        - Initialize context.
        - Parse declarative pipeline.
        - Create a list of strategies to run, explicitly adding `init` and `get`
          CalcFunctions.

        """
        self.ctx.current_id = 0
        pipeline: OTEPipelineData = self.ctx.pipeline

        # Outline pipeline
        if "run_pipeline" in self.inputs and self.inputs.run_pipeline:
            if self.inputs.run_pipeline.value in pipeline.pipelines:
                run_pipeline_name = self.inputs.run_pipeline.value
            else:
                raise InputValidationError(
                    f"{self.inputs.run_pipeline.value} not found in declarative "
                    "pipeline. Pipelines: "
                    f"{', '.join(repr(_) for _ in pipeline.pipelines)}"
                )
        elif len(pipeline.pipelines) != 1:
            raise ValidationError(
                f"{len(pipeline.pipelines)} pipelines given in the declarative "
                "pipeline. Please specify which pipeline to run through the "
                "'run_pipeline' input."
            )
        else:
            run_pipeline_name = list(pipeline.pipelines)[0]

        strategies = []
        # Initialization
        for strategy in pipeline.get_strategies(run_pipeline_name, reverse=True):
            strategies.append(
                (
                    "init",
                    strategy.get_type(),
                    self.ctx.strategy_configs[strategy.get_name()],
                )
            )
        # Getting
        for strategy in pipeline.get_strategies(run_pipeline_name):
            strategies.append(
                (
                    "get",
                    strategy.get_type(),
                    self.ctx.strategy_configs[strategy.get_name()],
                )
            )

        self.ctx.strategies = strategies

        self.ctx.ote_session = orm.Dict()

    def not_finished(self) -> bool:
        """Determine whether or not the WorkChain is finished.

        Returns:
            Whether or not the WorkChain is finished based on comparing the current
            strategy index in the list of strategies against the total number of
            strategies.

        """
        return self.ctx.current_id < len(self.ctx.strategies)

    def submit_next(self) -> None:
        """Prepare the current step for submission.

        Run the next strategy's CalcFunction and return its ProcessNode to the context.

        """
        strategy_method, strategy_type, strategy_config = self.ctx.strategies[
            self.ctx.current_id
        ]
        strategy_process_cls = (
            WorkflowFactory(f"execflow.{strategy_type}_{strategy_method}")
            if strategy_type in ("function", "transformation")
            else CalculationFactory(f"execflow.{strategy_type}_{strategy_method}")
        )

        self.to_context(
            current=run_get_node(
                strategy_process_cls,
                **{
                    "config": strategy_config,
                    "session": self.ctx.ote_session,
                },
            )[1]
        )

    def process_current(self) -> None:
        """Process the current step's Node.

        Report if the process did not finish OK.
        Retrieve the return session update object, update the session and store it back
        to the context for the next strategy to use.

        """
        if not self.ctx.current.is_finished_ok:
            self.report(
                f"A subprocess failed with exit status {self.ctx.current.exit_status}:"
                f" {self.ctx.current.exit_message}"
            )

        self.ctx.ote_session = (
            self.ctx.current.base.links.get_outgoing().get_node_by_label("result")
        )

        self.ctx.current_id += 1

    def finalize(self) -> None:
        """Finalize the WorkChain.

        Set the 'session' output.
        """
        self.out("session", self.ctx.ote_session)
