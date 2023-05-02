"""OTEAPI Download, Parse, and Resource strategy config AiiDA Data Node class."""
# pylint: disable=line-too-long,invalid-name
from typing import TYPE_CHECKING

from aiida.common.exceptions import ValidationError
from oteapi.models import ResourceConfig

from execflow.wrapper.data.genericconfig import GenericConfigData
from execflow.wrapper.data.secretconfig import SecretConfigData

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Optional, Union


class ResourceConfigData(GenericConfigData, SecretConfigData):
    """Resource Strategy Data Configuration.

    Important:
        Either of the pairs of attributes `downloadUrl`/`mediaType` or
        `accessUrl`/`accessService` MUST be specified.

    Args:
        downloadUrl (Optional[str]): Definition: The URL of the downloadable file in a
            given format. E.g. CSV file or RDF file.

            Usage: `downloadURL` *SHOULD* be used for the URL at
            which this distribution is available directly, typically through a HTTPS
            GET request or SFTP.
        mediaType (Optional[str]): The media type of the distribution as defined by IANA
            [[IANA-MEDIA-TYPES](https://www.w3.org/TR/vocab-dcat-2/#bib-iana-media-types)].

            Usage: This property *SHOULD* be used when the media type of the
            distribution is defined in IANA
            [[IANA-MEDIA-TYPES](https://www.w3.org/TR/vocab-dcat-2/#bib-iana-media-types)].
        accessUrl (Optional[str]): A URL of the resource that gives access to a
            distribution of the dataset. E.g. landing page, feed, SPARQL endpoint.

            Usage:

            - `accessURL` *SHOULD* be used for the URL of a service or location that
              can provide access to this distribution, typically through a Web form,
              query or API call.
            - `downloadURL` is preferred for direct links to downloadable resources.

        accessService (Optional[str]): A data service that gives access to the
            distribution of the dataset.
        license (Optional[str]): A legal document under which the distribution is made
            available.
        accessRights (Optional[str]): A rights statement that concerns how the
            distribution is accessed.
        publisher (Optional[str]): The entity responsible for making the resource/item
            available.

    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        downloadUrl: "Optional[str]" = None,
        mediaType: "Optional[str]" = None,
        accessUrl: "Optional[str]" = None,
        accessService: "Optional[str]" = None,
        license: "Optional[str]" = None,  # pylint: disable=redefined-builtin
        accessRights: "Optional[str]" = None,
        publisher: "Optional[str]" = None,
        **kwargs: "Any",
    ) -> None:
        if downloadUrl is None:
            downloadUrl = ResourceConfig.schema()["properties"]["downloadUrl"].get(
                "default"
            )

        if mediaType is None:
            mediaType = ResourceConfig.schema()["properties"]["mediaType"].get(
                "default"
            )

        if accessUrl is None:
            accessUrl = ResourceConfig.schema()["properties"]["accessUrl"].get(
                "default"
            )

        if accessService is None:
            accessService = ResourceConfig.schema()["properties"]["accessService"].get(
                "default"
            )

        if license is None:
            license = ResourceConfig.schema()["properties"]["license"].get("default")

        if accessRights is None:
            accessRights = ResourceConfig.schema()["properties"]["accessRights"].get(
                "default"
            )

        if publisher is None:
            publisher = ResourceConfig.schema()["properties"]["publisher"].get(
                "default"
            )

        super().__init__(**kwargs)

        attr_dict = {
            "downloadUrl": downloadUrl,
            "mediaType": mediaType,
            "accessUrl": accessUrl,
            "accessService": accessService,
            "license": license,
            "accessRights": accessRights,
            "publisher": publisher,
        }

        self.base.attributes.set_many(attr_dict)

    @property
    def downloadUrl(self) -> "Union[str, None]":
        """Definition: The URL of the downloadable file in a given format. E.g. CSV
        file or RDF file.

        Usage: `downloadURL` *SHOULD* be used for the URL at
        which this distribution is available directly, typically through a HTTPS
        GET request or SFTP.
        """
        return self.base.attributes.get("downloadUrl")

    @downloadUrl.setter
    def downloadUrl(self, value: "Union[str, None]") -> None:
        self.set_attribute("downloadUrl", value)

    @property
    def mediaType(self) -> "Union[str, None]":
        """The media type of the distribution as defined by IANA
        [[IANA-MEDIA-TYPES](https://www.w3.org/TR/vocab-dcat-2/#bib-iana-media-types)].

        Usage: This property *SHOULD* be used when the media
        type of the distribution is defined in IANA
        [[IANA-MEDIA-TYPES](https://www.w3.org/TR/vocab-dcat-2/#bib-iana-media-types)].
        """
        return self.base.attributes.get("mediaType")

    @mediaType.setter
    def mediaType(self, value: "Union[str, None]") -> None:
        self.set_attribute("mediaType", value)

    @property
    def accessUrl(self) -> "Union[str, None]":
        """A URL of the resource that gives access to a distribution of
        the dataset. E.g. landing page, feed, SPARQL endpoint.

        Usage:

        - `accessURL` *SHOULD* be used for the URL of a service or location that
           can provide access to this distribution, typically through a Web form,
           query or API call.
        - `downloadURL` is preferred for direct links to downloadable resources.

        """
        return self.base.attributes.get("accessUrl")

    @accessUrl.setter
    def accessUrl(self, value: "Union[str, None]") -> None:
        self.set_attribute("accessUrl", value)

    @property
    def accessService(self) -> "Union[str, None]":
        """A data service that gives access to the distribution of the dataset."""
        return self.base.attributes.get("accessService")

    @accessService.setter
    def accessService(self, value: "Union[str, None]") -> None:
        self.set_attribute("accessService", value)

    @property
    def license(self) -> "Union[str, None]":
        """A legal document under which the distribution is made available."""
        return self.base.attributes.get("license")

    @license.setter
    def license(self, value: "Union[str, None]") -> None:
        self.set_attribute("license", value)

    @property
    def accessRights(self) -> "Union[str, None]":
        """A rights statement that concerns how the distribution is accessed."""
        return self.base.attributes.get("accessRights")

    @accessRights.setter
    def accessRights(self, value: "Union[str, None]") -> None:
        self.set_attribute("accessRights", value)

    @property
    def publisher(self) -> "Union[str, None]":
        """The entity responsible for making the resource/item available."""
        return self.base.attributes.get("publisher")

    @publisher.setter
    def publisher(self, value: "Union[str, None]") -> None:
        self.set_attribute("publisher", value)

    def _validate(self) -> bool:
        """
        Check if either of the pairs of attributes `downloadUrl`/`mediaType` or
        `accessUrl`/`accessService` is specified.

        Raises:
            aiida.common.exceptions.ValidationError: If a valid pair of attributes
                cannot be determined.

        Returns:
            Whether or not the validation succeeded.

        """
        if (self.downloadUrl is None or self.mediaType is None) and (
            self.accessUrl is None or self.accessService is None
        ):
            raise ValidationError(
                "Either of the pairs of attributes downloadUrl/mediaType or "
                "accessUrl/accessService MUST be specified."
            )

        super()._validate()

        return True
