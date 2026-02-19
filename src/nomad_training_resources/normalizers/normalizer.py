from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad.config import config
from nomad.normalizing import Normalizer

from nomad_training_resources.schema_packages.schema_package import TrainingResource

configuration = config.get_plugin_entry_point(
    "nomad_training_resources.normalizers:normalizer_entry_point"
)

ENUM_LIST_FIELDS = [
    "instructional_method",
    "educational_level",
    "learning_resource_type",
    "format",
    "license",
    "subject",
]


def _as_list(value: Any) -> Optional[List[Any]]:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _dedupe_keep_order(values: List[str]) -> List[str]:
    out: List[str] = []
    for v in values:
        if v not in out:
            out.append(v)
    return out


def _preclean_enum_list(value: Any) -> Any:
    raw_list = _as_list(value)
    if raw_list is None:
        return None

    cleaned: List[str] = []
    for v in raw_list:
        if v is None:
            continue
        if not isinstance(v, str):
            v = str(v)
        s = v.strip()
        if not s:
            continue
        if s.lower() == "undefined":
            s = "Undefined"
        cleaned.append(s)

    cleaned = _dedupe_keep_order(cleaned)

    if not cleaned:
        return []

    if "Undefined" in cleaned and len(cleaned) > 1:
        cleaned = [v for v in cleaned if v != "Undefined"]

    return cleaned


class NewNormalizer(Normalizer):
    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        super().normalize(archive, logger)
        logger.info("NewNormalizer.normalize", parameter=configuration.parameter)

        data = archive.data
        if not isinstance(data, TrainingResource):
            return

        for field in ENUM_LIST_FIELDS:
            setattr(data, field, _preclean_enum_list(getattr(data, field, None)))
