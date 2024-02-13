"""A Data Node representing a declarative OTE pipeline."""

from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Type, Union

from aiida.common.exceptions import NotExistent, NotExistentAttributeError, ValidationError
from aiida.orm import Dict as DictNode
from aiida.orm import SinglefileData
from aiida.orm import Str as StrNode
from oteapi.models import FilterConfig, FunctionConfig, MappingConfig, ResourceConfig, TransformationConfig
from pydantic import BaseModel, Field, ValidationError, validator
import yaml

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple, Union


class DeclarativeStrategyBase(BaseModel):
    """A mix-in class for standard methods."""

    def get_type(self) -> str:
        """Get the type of strategy."""
        strategy_type = self.__class__.__name__[len("Declarative") :].lower()
        if not hasattr(self, strategy_type):
            raise ValueError(
                f"Cannot determine strategy type from {strategy_type!r}. Note, this "
                "function does not work from the DeclarativeStrategyBase mix-in class "
                "directly!"
            )
        return strategy_type

    def get_name(self) -> str:
        """Get the name of the strategy."""
        return getattr(self, self.get_type())

    def get_config(self) -> "Dict[str, Any]":
        """Get the model as a ready-to-parse config for AiiDA calculations."""
        return self.dict(exclude={self.get_type()})

    def __hash__(self) -> int:
        return hash(repr(self))


class DeclarativeDataResource(DeclarativeStrategyBase, ResourceConfig):
    """Data model for data resource."""

    dataresource: str = Field(
        ...,
        description="Name for the strategy within the declarative pipeline.",
    )


class DeclarativeFilter(DeclarativeStrategyBase, FilterConfig):
    """Data model for filter."""

    filter: str = Field(
        ...,
        description="Name for the strategy within the declarative pipeline.",
    )


class DeclarativeFunction(DeclarativeStrategyBase, FunctionConfig):
    """Data model for function."""

    function: str = Field(
        ...,
        description="Name for the strategy within the declarative pipeline.",
    )


class DeclarativeMapping(DeclarativeStrategyBase, MappingConfig):
    """Data model for mapping."""

    mapping: str = Field(
        ...,
        description="Name for the strategy within the declarative pipeline.",
    )


class DeclarativeTransformation(DeclarativeStrategyBase, TransformationConfig):
    """Data model for transformation."""

    transformation: str = Field(
        ...,
        description="Name for the strategy within the declarative pipeline.",
    )


if TYPE_CHECKING:  # pragma: no cover
    DeclarativeStrategy = Union[
        DeclarativeDataResource,
        DeclarativeFilter,
        DeclarativeFunction,
        DeclarativeMapping,
        DeclarativeTransformation,
    ]


class DeclarativePipeline(BaseModel):
    """Data model for a declarative pipeline."""

    version: int = Field(1, description="The declarative pipeline syntax version.")
    strategies: List[
        Union[
            DeclarativeDataResource,
            DeclarativeFilter,
            DeclarativeFunction,
            DeclarativeMapping,
            DeclarativeTransformation,
        ]
    ] = Field(
        ...,
        description=("List of strategies to be used in the pipeline(s), including their " "configuration."),
    )
    pipelines: Dict[str, str] = Field(
        ...,
        description="Dict of the pipeline(s) defined as part of the overall pipeline.",
    )

    @validator("strategies", pre=True, each_item=False)
    def type_cast_strategies(cls, value: "List[Dict[str, Any]]") -> "List[DeclarativeStrategy]":
        """Sort strategies into "correct" types."""
        type_mapping: "Dict[str, Type[DeclarativeStrategy]]" = {
            "dataresource": DeclarativeDataResource,
            "filter": DeclarativeFilter,
            "function": DeclarativeFunction,
            "mapping": DeclarativeMapping,
            "transformation": DeclarativeTransformation,
        }
        type_casted_strategies: "List[DeclarativeStrategy]" = []
        for strategy in value:
            for strategy_type, strategy_cls in type_mapping.items():
                if strategy_type in strategy:
                    try:
                        type_casted_strategies.append(strategy_cls(**strategy))
                    except ValidationError as exc:
                        exc_message = str(exc).replace("\n", "\n  ")
                        raise ValueError(
                            "Strategy cannot be validated as a "
                            f"{strategy_cls.__name__!r}."
                            f"\n  strategy: {strategy}\n  {exc_message}"
                        ) from exc
                    break
            else:
                raise ValueError(
                    "Strategy does not define a valid strategy type as key:"
                    f"\n  strategy: {strategy}\n  Valid types: {type_mapping}"
                )
        return type_casted_strategies

    @validator("pipelines")
    def ensure_steps_exist(cls, value: "Dict[str, str]", values: "Dict[str, Any]") -> "Dict[str, str]":
        """Ensure the listed steps in the pipelines exist within the same data model."""
        strategy_names = [strategy.get_name() for strategy in values.get("strategies", [])]
        pipeline_names = list(value)
        for name, pipeline in value.items():
            pipeline_parts = [part.strip() for part in pipeline.split("|")]
            if not all(part in strategy_names + pipeline_names for part in pipeline_parts):
                raise ValueError(
                    f"Part(s) in {name!r} pipeline not found in the list of strategies"
                    " or pipelines within the declarative pipeline."
                )
        return value

    def _strategy_names(self) -> "List[str]":
        """Utility function to return list of strategy names.

        Returns:
            List of strategy names as given in the declarative pipeline.

        """
        return [strategy.get_name() for strategy in self.strategies]

    def get_strategy(self, strategy_name: str) -> "DeclarativeStrategy":
        """Get a strategy based on its given name.

        Parameters:
            strategy_name: The name given the strategy in the declarative pipeline.

        Returns:
            The declarative strategy model object with the given name.

        """
        for strategy in self.strategies:
            if strategy_name == strategy.get_name():
                return strategy
        raise ValueError(f"Strategy {strategy_name!r} does not exist among {self._strategy_names()}")

    def parse_pipeline(self, pipeline: str) -> "List[DeclarativeStrategy]":
        """Resolve a pipeline into its strategy parts.

        Parameters:
            pipeline: Name of the pipeline.

        Returns:
            (Ordered) list of strategies in the pipeline.

        """
        if pipeline not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline!r} does not exist among {list(self.pipelines)}")

        parsed_pipeline = []

        pipeline_parts = [part.strip() for part in self.pipelines[pipeline].split("|")]
        for part in pipeline_parts:
            if part in self._strategy_names():
                parsed_pipeline.append(self.get_strategy(part))
            elif part in self.pipelines:
                parsed_pipeline.extend(self.parse_pipeline(part))
            else:
                raise ValueError(
                    f"Could unexpectedly not find part {part!r} in the list of known " "strategy and pipeline names!"
                )
        return parsed_pipeline

    def __hash__(self) -> int:
        return hash(repr(self))


class OTEPipelineData(DictNode):
    """An OTE pipeline.

    The data structure is based on the declarative pipeline syntax.

    Strategy for initializing:

    - Either `value` or either of `filepath` and `single_file` are defined.
    - All explicit top keywords either modify now existing top keywords or create them.

    """

    _pydantic_model_class = DeclarativePipeline
    _pydantic_model_hash = None
    _pydantic_model = None

    def __init__(  # pylint: disable=too-many-branches,too-many-statements
        self,
        # From dict
        value: "Optional[Union[Dict[str, Any], OTEPipelineData, DictNode, DeclarativePipeline, str, bytes, StrNode]]" = None,  # pylint: disable=line-too-long
        # From file
        filepath: "Optional[Union[Path, str, StrNode]]" = None,
        single_file: "Optional[SinglefileData]" = None,
        # Explicitly - top keywords
        version: "Optional[Union[int, str]]" = None,
        strategies: "Optional[List[Dict[str, Any]]]" = None,
        pipelines: "Optional[Dict[str, str]]" = None,
        # AiiDA-specific extra keyword-arguments
        **kwargs: "Any",
    ) -> None:
        # Update
        dictionary = None

        if value is not None:
            dictionary = deepcopy(value)

        if dictionary is None:
            if filepath and single_file:
                raise ValueError("Specify either 'filepath' or 'single_file', not both.")
            if filepath:
                filepath = Path(filepath.value).resolve() if isinstance(filepath, StrNode) else Path(filepath).resolve()
                if not filepath.exists():
                    raise FileNotFoundError(f"Cannot find file at filepath={filepath}")
                try:
                    dictionary = yaml.safe_load(filepath.read_bytes())
                except yaml.error.YAMLError as exc:
                    raise ValueError(
                        "Could not parse declarative pipeline YAML file from " f"filepath={filepath}."
                    ) from exc
            elif single_file:
                try:
                    dictionary = yaml.safe_load(single_file.get_content())
                except yaml.error.YAMLError as exc:
                    raise ValueError(
                        "Could not parse declarative pipeline YAML file from " f"single_file={single_file}."
                    ) from exc

        if dictionary and isinstance(dictionary, (str, bytes, StrNode)):
            try:
                dictionary = (
                    yaml.safe_load(dictionary.value) if isinstance(dictionary, StrNode) else yaml.safe_load(dictionary)
                )
            except yaml.error.YAMLError as exc:
                raise ValueError("Could not parse declarative pipeline YAML file from 'value'.") from exc

        if dictionary and isinstance(dictionary, self._pydantic_model_class):
            dictionary = dictionary.dict()

        dictionary = dictionary or {}

        if not isinstance(dictionary, (dict, DictNode)):
            raise ValidationError(
                "dictionary should now be a Python/AiiDA dict. Instead it is a "
                f"{type(dictionary)!r}. Content:\n\n{dictionary}"
            )

        if "version" in dictionary:
            try:
                dictionary["version"] = int(dictionary["version"])
            except ValueError as exc:
                raise ValueError(f"{dictionary['version']!r} is not a valid value for 'version'.") from exc

        if version is not None:
            try:
                version = int(version)
            except ValueError as exc:
                raise ValueError(f"{version!r} is not a valid value for 'version'.") from exc
            dictionary["version"] = version

        if strategies is not None:
            if "strategies" in dictionary:
                original_strategies = dictionary["strategies"]
                for strategy in list(strategies):
                    if strategy in original_strategies:
                        strategies.remove(strategy)
                dictionary["strategies"] = dictionary["strategies"].extend(strategies)
            else:
                dictionary["strategies"] = strategies

        if pipelines is not None:
            if "pipelines" in dictionary:
                updated_pipelines: "Dict[str, str]" = dictionary["pipelines"]
                updated_pipelines.update(pipelines)
                dictionary["pipelines"] = updated_pipelines
            else:
                dictionary["pipelines"] = pipelines

        super().__init__(value=dictionary, **kwargs)
        self.validate()

    def validate(self, strict: bool = False) -> None:
        """Validate the internal data model via the pydantic data model.

        Parameters:
            strict: Whether or not to raise if `strategies` or `pipelines` are None.

        """
        if self.base.attributes.get("strategies", None) and self.base.attributes.get("pipelines", None):
            self._pydantic_model = self._pydantic_model_class(**self.get_dict())
            self._pydantic_model_hash = hash(self._pydantic_model)
        elif strict:
            raise ValidationError(
                "Cannot validate, missing"
                f"{' strategies' if self.base.attributes.get('strategies', None) is None else ''}"  # pylint: disable=line-too-long
                f"{' and' if self.base.attributes.get('strategies', None) is None and self.base.attributes.get('pipelines', None) is None else ''}"  # pylint: disable=line-too-long
                f"{' pipelines' if self.base.attributes.get('pipelines', None) is None else ''}"
            )

    @property
    def version(self) -> int:
        """Return the declarative pipeline syntax version.

        Returns:
            The declarative pipeline syntax version.

        Raises:
            NotExistentAttributeError: If
                :py:attr:`~execflow.data.oteapi.OTEPipelineData.version` is not
                defined.

        """
        try:
            return self.base.attributes.get("version")
        except AttributeError as exc:
            raise NotExistentAttributeError("version is not defined.") from exc

    @version.setter
    def version(self, value: int) -> None:
        """Set the version.

        Parameters:
            value: The version to store.

        """
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise TypeError("'value' must be an integer.") from exc
        self["version"] = value

    @property
    def strategies(self) -> "List[Dict[str, Any]]":
        """Return a stand-alone list of strategies.

        By "stand-alone" it is meant that mutating the returned list, will not result
        in changes in the strategies stored within the Node.

        Example:
            To extend the strategies in the OTEPipelineData Node `node` with a list
            of strategies `my_extra_strategies`, you can do:

            .. code:: python

               node["strategies"] = node["strategies"].extend(my_extra_strategies)

            or

            .. code:: python

                node.dict.strategies = node.dict.strategies.extend(my_extra_strategies)

            or a mix of these approaches.

        Returns:
            The list of strategies.

        Raises:
            NotExistentAttributeError: If
                :py:attr:`~execflow.data.oteapi.OTEPipelineData.strategies` is not
                defined.

        """
        try:
            return self.base.attributes.get("strategies")
        except AttributeError as exc:
            raise NotExistentAttributeError("strategies is not defined.") from exc

    @strategies.setter
    def strategies(self, value: "Iterable[Dict[str, Any]]") -> None:
        """Set the list of strategies.

        Parameters:
            value: The list of strategies to store.

        """
        try:
            value = list(value)
        except (TypeError, ValueError) as exc:
            raise TypeError("'value' must be an iterable of dictionaries.") from exc
        self["strategies"] = value

    @property
    def pipelines(self) -> "Dict[str, Any]":
        """Return a stand-alone dictionary of pipelines.

        By "stand-alone" it is meant that mutating the returned dictionary, will not
        result in changes in the pipelines stored within the Node.

        Example:
            To update the pipelines in the OTEPipelineData Node `node` with a
            dictionary of pipelines `my_updated_pipelines`, you can do:

            .. code:: python

                updated_pipelines = node["pipelines"]
                updated_pipelines.update(my_updated_pipelines)
                node["pipelines"] = updated_pipelines

            or

            .. code:: python

                updated_pipelines = node.dict.pipelines
                updated_pipelines.update(my_updated_pipelines)
                node.dict.pipelines = updated_pipelines

            or a mix of these approaches.

            Note, from Python 3.9 the above example can be simplified to:

            .. code:: python

                node.dict.pipelines = node["pipelines"] | my_updated_pipelines

        Returns:
            The pipelines or `None` if no pipelines have been set.

        Raises:
            NotExistentAttributeError: If
                :py:attr:`~execflow.data.oteapi.OTEPipelineData.pipelines` is not
                defined.


        """
        try:
            return self.base.attributes.get("pipelines")
        except AttributeError as exc:
            raise NotExistentAttributeError("pipelines is not defined.") from exc

    @pipelines.setter
    def pipelines(self, value: "Union[Dict[str, str], Iterable[Tuple[str, str]]]") -> None:
        """Set the dictionary of pipelines.

        Parameters:
            value: The dictionary of pipelines to store.

        """
        try:
            value = dict(value)
        except (TypeError, ValueError) as exc:
            raise TypeError("'value' must be a dictionary.") from exc
        self["pipelines"] = value

    @property
    def pydantic_model(self) -> "DeclarativePipeline":
        """Instantiate and return a pydantic model of the declarative pipeline.

        Returns:
            A pydantic model representing the declarative pipeline.

        """
        if self.base.attributes.get("strategies", None) is None or self.base.attributes.get("pipelines", None) is None:
            raise NotExistent(
                "Cannot instantiate a pydantic model, missing"
                f"{' strategies' if self.base.attributes.get('strategies', None) is None else ''}"  # pylint: disable=line-too-long
                f"{' and' if self.base.attributes.get('strategies', None) is None and self.base.attributes.get('pipelines') is None else ''}"  # pylint: disable=line-too-long
                f"{' pipelines' if self.base.attributes.get('pipelines', None) is None else ''}"
            )

        if self._pydantic_model_hash is None or self._pydantic_model_hash != hash(self._pydantic_model):
            self._pydantic_model = self._pydantic_model_class(**self.get_dict())
            self._pydantic_model_hash = hash(self._pydantic_model)

        if not isinstance(self._pydantic_model, self._pydantic_model_class):
            raise ValidationError("Internal pydantic model not set!")

        return self._pydantic_model

    def get_strategies(self, pipeline: str, reverse: bool = False) -> "Generator[DeclarativeStrategy, None, None]":
        """Yield pipeline strategies as pydantic models.

        Parameters:
            pipeline: The pipeline name to iterate over / resolve.
            reverse: Whether or not to iterate over / resolve the pipeline in reverse.

        Yields:
            A declarative strategy model object.

        """
        self.validate(strict=True)
        if self.base.attributes.get("pipelines", None) and pipeline not in self.pipelines:
            raise NotExistent(f"Pipeline {pipeline!r} does not exist among {list(self.pipelines)}")

        if reverse:
            for strategy in reversed(self.pydantic_model.parse_pipeline(pipeline)):
                yield strategy
        else:
            for strategy in self.pydantic_model.parse_pipeline(pipeline):
                yield strategy
