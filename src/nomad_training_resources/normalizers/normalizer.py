from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad.config import config
from nomad.normalizing import Normalizer

from nomad_training_resources.schema_packages.schema_package import TrainingResource

# Load the normalizer configuration from the plugin entry point.
configuration = config.get_plugin_entry_point(
    "nomad_training_resources.normalizers:normalizer_entry_point"
)


def _is_empty(value) -> bool:
    """
    Return True if a quantity should be treated as 'missing/empty'.

    - None
    - empty list / tuple
    - list / tuple with only None / empty strings
    - empty / whitespace-only string
    """
    if value is None:
        return True

    # Strings
    if isinstance(value, str):
        return value.strip() == ""

    # Lists / tuples (we only have lists)
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return True
        # All elements empty / None / whitespace
        return all(
            (v is None) or (isinstance(v, str) and v.strip() == "")
            for v in value
        )

    # Anything else: treat as "has some value"
    return False


def _clean_undefined(value):
    """
    Normalize placeholder values like 'undefined' / 'Undefined' so that
    `_is_empty` can treat them as missing.

    - For strings: 'undefined' (any case) -> None
    - For lists/tuples: remove all 'undefined'-like items
    """
    if value is None:
        return None

    if isinstance(value, str):
        return None if value.strip().lower() == "undefined" else value

    if isinstance(value, (list, tuple)):
        cleaned = [
            v
            for v in value
            if not (isinstance(v, str) and v.strip().lower() == "undefined")
        ]
        return cleaned

    return value


class NewNormalizer(Normalizer):
    """
    Plugin normalizer for the nomad_training_resources package.

    It:
    - logs that it ran (using the template configuration),
    - sets 'Undefined' for controlled-vocabulary fields when they are empty
      or contain only 'undefined'-like markers.
    """

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        super().normalize(archive, logger)
        print('here i am mashti')

        logger.info("NewNormalizer.normalize", parameter=configuration.parameter)

        data = archive.data
        if not isinstance(data, TrainingResource):
            return

        subjects = _clean_undefined(getattr(data, "subject", None))
        if _is_empty(subjects):
            data.subject = ["Undefined"]
        else:
            data.subject = subjects

        keywords = _clean_undefined(getattr(data, "keywords", None))
        if _is_empty(keywords):
            data.keywords = ["Undefined"]
        else:
            data.keywords = keywords

        instructional_methods = _clean_undefined(
            getattr(data, "instructional_method", None)
        )
        if _is_empty(instructional_methods):
            data.instructional_method = ["Undefined"]
        else:
            data.instructional_method = instructional_methods

        educational_levels = _clean_undefined(
            getattr(data, "educational_level", None)
        )
        if _is_empty(educational_levels):
            data.educational_level = ["Undefined"]
        else:
            data.educational_level = educational_levels

        lrt = _clean_undefined(getattr(data, "learning_resource_type", None))
        if _is_empty(lrt):
            data.learning_resource_type = "Undefined"
        else:
            data.learning_resource_type = lrt

        fmt = _clean_undefined(getattr(data, "format", None))
        if _is_empty(fmt):
            data.format = "Undefined"
        else:
            data.format = fmt

        lic = _clean_undefined(getattr(data, "license", None))
        if _is_empty(lic):
            data.license = "Undefined"
        else:
            data.license = lic
