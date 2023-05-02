"""A Data Node representing a declarative OTE pipeline."""
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from aiida.common.exceptions import (
    NotExistent,
    NotExistentAttributeError,
    ValidationError,
)
from aiida.orm import Dict as DictNode
from aiida.orm import SinglefileData
from aiida.orm import Str as StrNode

from execflow.utils import DeclarativePipeline

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple, Union

    from execflow.utils import DeclarativeStrategy


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
                raise ValueError(
                    "Specify either 'filepath' or 'single_file', not both."
                )
            if filepath:
                filepath = (
                    Path(filepath.value).resolve()
                    if isinstance(filepath, StrNode)
                    else Path(filepath).resolve()
                )
                if not filepath.exists():
                    raise FileNotFoundError(f"Cannot find file at filepath={filepath}")
                try:
                    dictionary = yaml.safe_load(filepath.read_bytes())
                except yaml.error.YAMLError as exc:
                    raise ValueError(
                        "Could not parse declarative pipeline YAML file from "
                        f"filepath={filepath}."
                    ) from exc
            elif single_file:
                try:
                    dictionary = yaml.safe_load(single_file.get_content())
                except yaml.error.YAMLError as exc:
                    raise ValueError(
                        "Could not parse declarative pipeline YAML file from "
                        f"single_file={single_file}."
                    ) from exc

        if dictionary and isinstance(dictionary, (str, bytes, StrNode)):
            try:
                dictionary = (
                    yaml.safe_load(dictionary.value)
                    if isinstance(dictionary, StrNode)
                    else yaml.safe_load(dictionary)
                )
            except yaml.error.YAMLError as exc:
                raise ValueError(
                    "Could not parse declarative pipeline YAML file from 'value'."
                ) from exc

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
                raise ValueError(
                    f"{dictionary['version']!r} is not a valid value for 'version'."
                ) from exc

        if version is not None:
            try:
                version = int(version)
            except ValueError as exc:
                raise ValueError(
                    f"{version!r} is not a valid value for 'version'."
                ) from exc
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
        if self.base.attributes.get("strategies", None) and self.base.attributes.get(
            "pipelines", None
        ):
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
                :py:attr:`~execflow.wrapper.data.OTEPipelineData.version` is not
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
                :py:attr:`~execflow.wrapper.data.OTEPipelineData.strategies` is not
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
                :py:attr:`~execflow.wrapper.data.OTEPipelineData.pipelines` is not
                defined.


        """
        try:
            return self.base.attributes.get("pipelines")
        except AttributeError as exc:
            raise NotExistentAttributeError("pipelines is not defined.") from exc

    @pipelines.setter
    def pipelines(
        self, value: "Union[Dict[str, str], Iterable[Tuple[str, str]]]"
    ) -> None:
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
        if (
            self.base.attributes.get("strategies", None) is None
            or self.base.attributes.get("pipelines", None) is None
        ):
            raise NotExistent(
                "Cannot instantiate a pydantic model, missing"
                f"{' strategies' if self.base.attributes.get('strategies', None) is None else ''}"  # pylint: disable=line-too-long
                f"{' and' if self.base.attributes.get('strategies', None) is None and self.base.attributes.get('pipelines') is None else ''}"  # pylint: disable=line-too-long
                f"{' pipelines' if self.base.attributes.get('pipelines', None) is None else ''}"
            )

        if self._pydantic_model_hash is None or self._pydantic_model_hash != hash(
            self._pydantic_model
        ):
            self._pydantic_model = self._pydantic_model_class(**self.get_dict())
            self._pydantic_model_hash = hash(self._pydantic_model)

        if not isinstance(self._pydantic_model, self._pydantic_model_class):
            raise ValidationError("Internal pydantic model not set!")

        return self._pydantic_model

    def get_strategies(
        self, pipeline: str, reverse: bool = False
    ) -> "Generator[DeclarativeStrategy, None, None]":
        """Yield pipeline strategies as pydantic models.

        Parameters:
            pipeline: The pipeline name to iterate over / resolve.
            reverse: Whether or not to iterate over / resolve the pipeline in reverse.

        Yields:
            A declarative strategy model object.

        """
        self.validate(strict=True)
        if (
            self.base.attributes.get("pipelines", None)
            and pipeline not in self.pipelines
        ):
            raise NotExistent(
                f"Pipeline {pipeline!r} does not exist among {list(self.pipelines)}"
            )

        if reverse:
            for strategy in reversed(self.pydantic_model.parse_pipeline(pipeline)):
                yield strategy
        else:
            for strategy in self.pydantic_model.parse_pipeline(pipeline):
                yield strategy
