"""OTEAPI Transformation strategy config AiiDA Data Node class."""
# pylint: disable=invalid-name
from typing import TYPE_CHECKING

from oteapi.models.transformationconfig import (
    TransformationConfig,
    TransformationStatus,
)

from execflow.wrapper.data.base import ExtendedData
from execflow.wrapper.data.genericconfig import GenericConfigData
from execflow.wrapper.data.secretconfig import SecretConfigData

if TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime
    from typing import Any, Optional, Union

    from oteapi.models.transformationconfig import ProcessPriority


class TransformationConfigData(GenericConfigData, SecretConfigData):
    """Transformation Strategy Data Configuration.

    Args:
        transformationType (str): Type of registered transformation strategy.
            E.g., `celery/remote`.
        name (Optional[str]): Human-readable name of the transformation strategy.
        due (Optional[datetime]): Optional field to indicate a due data/time for when a
            transformation should finish.
        priority (Optional[ProcessPriority]): Define the process priority of the
            transformation execution.
        secret (Optional[str]): Authorization secret given when running a
            transformation.

    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        transformationType: str,
        name: "Optional[str]" = None,
        due: "Optional[datetime]" = None,
        priority: "Optional[ProcessPriority]" = None,
        **kwargs: "Any",
    ) -> None:
        if name is None:
            name = TransformationConfig.schema()["properties"]["name"].get("default")

        if due is None:
            due = TransformationConfig.schema()["properties"]["due"].get("default")

        if priority is None:
            priority = TransformationConfig.schema()["properties"]["priority"].get(
                "default"
            )

        super().__init__(**kwargs)

        attr_dict = {
            "transformationType": transformationType,
            "name": name,
            "due": due,
            "priority": priority,
        }

        self.base.attributes.set_many(attr_dict)

    @property
    def transformationType(self) -> str:
        """Type of registered transformation strategy. E.g., `celery/remote`."""
        return self.base.attributes.get("transformationType")

    @transformationType.setter
    def transformationType(self, value: str) -> None:
        self.set_attribute("transformationType", value)

    @property
    def name(self) -> "Union[str, None]":
        """Human-readable name of the transformation strategy."""
        return self.base.attributes.get("name")

    @name.setter
    def name(self, value: "Union[str, None]") -> None:
        self.set_attribute("name", value)

    @property
    def due(self) -> "Union[datetime, None]":
        """Optional field to indicate a due data/time for when a transformation should
        finish."""
        return self.base.attributes.get("due")

    @due.setter
    def due(self, value: "Union[datetime, None]") -> None:
        self.set_attribute("due", value)

    @property
    def priority(self) -> "Union[ProcessPriority, None]":
        """Define the process priority of the transformation execution."""
        return self.base.attributes.get("priority")

    @priority.setter
    def priority(self, value: "Union[ProcessPriority, None]") -> None:
        self.set_attribute("priority", value)


class TransformationStatusData(ExtendedData):
    """Return from transformation status.

    Args:
        id (str): ID for the given transformation process.
        status (Optional[str]): Status for the transformation process.
        messages (Optional[list[str]]): Messages related to the transformation process.
        created (Optional[datetime]): Time of creation for the transformation process.
            Given in UTC.
        startTime (Optional[datetime]): Time when the transformation process started.
            Given in UTC.
        finishTime (Optional[datetime]): Time when the tranformation process finished.
            Given in UTC.

    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        id: str,  # pylint: disable=redefined-builtin
        status: "Optional[str]" = None,
        messages: "Optional[list[str]]" = None,
        created: "Optional[datetime]" = None,
        startTime: "Optional[datetime]" = None,
        finishTime: "Optional[datetime]" = None,
        **kwargs: "Any",
    ) -> None:
        if status is None:
            status = TransformationStatus.schema()["properties"]["status"].get(
                "default"
            )

        if messages is None:
            messages = TransformationStatus.schema()["properties"]["messages"].get(
                "default"
            )

        if created is None:
            created = TransformationStatus.schema()["properties"]["created"].get(
                "default"
            )

        if startTime is None:
            startTime = TransformationStatus.schema()["properties"]["startTime"].get(
                "default"
            )

        if finishTime is None:
            finishTime = TransformationStatus.schema()["properties"]["finishTime"].get(
                "default"
            )

        super().__init__(**kwargs)

        attr_dict = {
            "id": id,
            "status": status,
            "messages": messages,
            "created": created,
            "startTime": startTime,
            "finishTime": finishTime,
        }

        self.base.attributes.set_many(attr_dict)

    @property
    def id(self) -> str:
        """ID for the given transformation process."""
        return self.base.attributes.get("id")

    @id.setter
    def id(self, value: str) -> None:
        self.set_attribute("id", value)

    @property
    def status(self) -> "Union[str, None]":
        """Status for the transformation process."""
        return self.base.attributes.get("status")

    @status.setter
    def status(self, value: "Union[str, None]") -> None:
        self.set_attribute("status", value)

    @property
    def messages(self) -> "Union[list[str], None]":
        """Messages related to the transformation process."""
        return self.base.attributes.get("messages")

    @messages.setter
    def messages(self, value: "Union[list[str], None]") -> None:
        self.set_attribute("messages", value)

    @property
    def created(self) -> "Union[datetime, None]":
        """Time of creation for the transformation process. Given in UTC."""
        return self.base.attributes.get("created")

    @created.setter
    def created(self, value: "Union[datetime, None]") -> None:
        self.set_attribute("created", value)

    @property
    def startTime(self) -> "Union[datetime, None]":
        """Time when the transformation process started. Given in UTC."""
        return self.base.attributes.get("startTime")

    @startTime.setter
    def startTime(self, value: "Union[datetime, None]") -> None:
        self.set_attribute("startTime", value)

    @property
    def finishTime(self) -> "Union[datetime, None]":
        """Time when the tranformation process finished. Given in UTC."""
        return self.base.attributes.get("finishTime")

    @finishTime.setter
    def finishTime(self, value: "Union[datetime, None]") -> None:
        self.set_attribute("finishTime", value)
