"""OTEAPI Transformation strategy config AiiDA Data Node class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oteapi.models.transformationconfig import (
    TransformationConfig,
    TransformationStatus,
)

from execflow.data.oteapi.base import ExtendedData
from execflow.data.oteapi.genericconfig import GenericConfigData
from execflow.data.oteapi.secretconfig import SecretConfigData

if TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime
    from typing import Any

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

    def __init__(
        self,
        transformationType: str,
        name: str | None = None,
        due: datetime | None = None,
        priority: ProcessPriority | None = None,
        **kwargs: Any,
    ) -> None:
        if name is None:
            name = TransformationConfig.model_fields["name"].default

        if due is None:
            due = TransformationConfig.model_fields["due"].default

        if priority is None:
            priority = TransformationConfig.model_fields["priority"].default

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
    def name(self) -> str | None:
        """Human-readable name of the transformation strategy."""
        return self.base.attributes.get("name")

    @name.setter
    def name(self, value: str | None) -> None:
        self.set_attribute("name", value)

    @property
    def due(self) -> datetime | None:
        """Optional field to indicate a due data/time for when a transformation should
        finish."""
        return self.base.attributes.get("due")

    @due.setter
    def due(self, value: datetime | None) -> None:
        self.set_attribute("due", value)

    @property
    def priority(self) -> ProcessPriority | None:
        """Define the process priority of the transformation execution."""
        return self.base.attributes.get("priority")

    @priority.setter
    def priority(self, value: ProcessPriority | None) -> None:
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

    def __init__(
        self,
        id: str,
        status: str | None = None,
        messages: list[str] | None = None,
        created: datetime | None = None,
        startTime: datetime | None = None,
        finishTime: datetime | None = None,
        **kwargs: Any,
    ) -> None:
        if status is None:
            status = TransformationStatus.model_fields["status"].default

        if messages is None:
            messages = TransformationStatus.model_fields["messages"].default

        if created is None:
            created = TransformationStatus.model_fields["created"].default

        if startTime is None:
            startTime = TransformationStatus.model_fields["startTime"].default

        if finishTime is None:
            finishTime = TransformationStatus.model_fields["finishTime"].default

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
    def status(self) -> str | None:
        """Status for the transformation process."""
        return self.base.attributes.get("status")

    @status.setter
    def status(self, value: str | None) -> None:
        self.set_attribute("status", value)

    @property
    def messages(self) -> list[str] | None:
        """Messages related to the transformation process."""
        return self.base.attributes.get("messages")

    @messages.setter
    def messages(self, value: list[str] | None) -> None:
        self.set_attribute("messages", value)

    @property
    def created(self) -> datetime | None:
        """Time of creation for the transformation process. Given in UTC."""
        return self.base.attributes.get("created")

    @created.setter
    def created(self, value: datetime | None) -> None:
        self.set_attribute("created", value)

    @property
    def startTime(self) -> datetime | None:
        """Time when the transformation process started. Given in UTC."""
        return self.base.attributes.get("startTime")

    @startTime.setter
    def startTime(self, value: datetime | None) -> None:
        self.set_attribute("startTime", value)

    @property
    def finishTime(self) -> datetime | None:
        """Time when the tranformation process finished. Given in UTC."""
        return self.base.attributes.get("finishTime")

    @finishTime.setter
    def finishTime(self, value: datetime | None) -> None:
        self.set_attribute("finishTime", value)
