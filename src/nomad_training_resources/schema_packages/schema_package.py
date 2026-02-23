from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterable, List, Optional
from urllib.parse import parse_qs, urlencode, urlparse

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad.config import config
from nomad.datamodel.data import ArchiveSection, Schema
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.datamodel.results import ELN, Results
from nomad.metainfo import Datetime, MEnum, Quantity, SchemaPackage, Section, SubSection

configuration = config.get_plugin_entry_point(
    "nomad_training_resources.schema_packages:training_resources_schema"
)

m_package = SchemaPackage()

INSTRUCTIONAL_METHODS = ["Tutorial", "How To", "Explanation", "Reference", "Undefined"]
EDUCATIONAL_LEVELS = ["Beginner", "Intermediate", "Advanced", "Undefined"]
LEARNING_RESOURCE_TYPES = [
    "FAIRmat Tutorial",
    "NOMAD Documentation",
    "Git Repo",
    "NOMAD Examples",
    "Self Learning",
    "Undefined",
]
FORMATS = [
    "Video File",
    "Technical Article",
    "Presentation Document",
    "Software Application",
    "Source Code",
    "Undefined",
]
LICENSES = ["CC0", "CC BY", "MIT License", "Apache License 2.0", "GNU GPLv3", "Undefined"]
SUBJECTS = [
    "General NOMAD",
    "Publish",
    "Explore",
    "Analyze",
    "ELN",
    "API",
    "Oasis Customization",
    "Oasis Installation",
    "Oasis Configuration",
    "NOMAD Plugins",
    "Develop NOMAD",
    "NeXus",
    "General RDM",
    "Scientific Use Cases",
    "CAMELS",
    "NOMAD CAMELS",
    "NOMAD Encyclopedia",
    "AI",
    "Undefined",
]

RELATION_TYPES = [
    "sameAs",
    "isPartOf",
    "hasPart",
    "isFormatOf",
    "hasFormat",
    "isReplacedBy",
    "replaces",
    "isReferencedBy",
    "references",
    "isBasedOn",
]

RELATION_STATUS = [
    "manual_reference",
    "resolved_from_identifier",
    "identifier_not_found",
    "identifier_ambiguous",
    "identifier_missing",
    "skipped_client_context",
    "error",
]


def _unique_clean(values: Optional[Iterable[str]]) -> List[str]:
    out: List[str] = []
    for v in values or []:
        if v is None:
            continue
        if isinstance(v, str):
            v = v.strip()
        if not v:
            continue
        if v not in out:
            out.append(v)
    return out


def _normalize_enum_list(values: Optional[Iterable[str]]) -> List[str]:
    cleaned = _unique_clean(values)
    if not cleaned:
        return ["Undefined"]
    if "Undefined" in cleaned and len(cleaned) > 1:
        cleaned = [v for v in cleaned if v != "Undefined"]
    return cleaned


def _normalize_enum_list_client(values: Optional[Iterable[str]]) -> List[str]:
    cleaned = _unique_clean(values)
    if not cleaned:
        return []
    if "Undefined" in cleaned:
        if len(cleaned) == 1:
            return []
        return [v for v in cleaned if v != "Undefined"]
    return cleaned


def _normalize_free_list(values: Optional[Iterable[str]]) -> List[str]:
    return _unique_clean(values)


_YOUTUBE_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def _canonicalize_youtube_url(url: str) -> Optional[str]:
    if url is None:
        return None
    s = url.strip()
    if s == "":
        return None

    if not (s.startswith("http://") or s.startswith("https://")):
        if (
            s.startswith("youtu.be/")
            or s.startswith("www.youtube.com/")
            or s.startswith("youtube.com/")
            or s.startswith("m.youtube.com/")
            or s.startswith("music.youtube.com/")
        ):
            s = "https://" + s
        else:
            return None

    try:
        u = urlparse(s)
    except Exception:
        return None

    host = (u.netloc or "").lower()
    if not host:
        return None

    is_youtube = ("youtube.com" in host) or ("youtu.be" in host)
    if not is_youtube:
        return None

    qs = parse_qs(u.query)
    path = u.path or ""

    playlist_id = None
    if "list" in qs and qs["list"]:
        playlist_id = (qs["list"][0] or "").strip() or None

    video_id = None
    if "v" in qs and qs["v"]:
        video_id = (qs["v"][0] or "").strip() or None

    if video_id is None and "youtu.be" in host:
        seg = path.strip("/").split("/")[0] if path.strip("/") else ""
        video_id = seg.strip() or None

    if video_id is None:
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"shorts", "embed", "live", "v"}:
            video_id = (parts[1] or "").strip() or None

    if video_id is not None and not _YOUTUBE_VIDEO_ID_RE.match(video_id):
        video_id = None

    if video_id:
        return f"https://www.youtube.com/watch?{urlencode({'v': video_id})}"

    if playlist_id:
        return f"https://www.youtube.com/playlist?{urlencode({'list': playlist_id})}"

    return None


def _canonicalize_identifier(url: Optional[str]) -> Optional[str]:
    if url is None:
        return None
    s = url.strip()
    if s == "":
        return s

    yt = _canonicalize_youtube_url(s)
    if yt is not None:
        return yt

    return s


class InstructionalMethodTerm(ArchiveSection):
    m_def = Section(a_eln={"hide": ["value"]})
    value = Quantity(type=MEnum(INSTRUCTIONAL_METHODS))


class EducationalLevelTerm(ArchiveSection):
    m_def = Section(a_eln={"hide": ["value"]})
    value = Quantity(type=MEnum(EDUCATIONAL_LEVELS))


class LearningResourceTypeTerm(ArchiveSection):
    m_def = Section(a_eln={"hide": ["value"]})
    value = Quantity(type=MEnum(LEARNING_RESOURCE_TYPES))


class FormatTerm(ArchiveSection):
    m_def = Section(a_eln={"hide": ["value"]})
    value = Quantity(type=MEnum(FORMATS))


class LicenseTerm(ArchiveSection):
    m_def = Section(a_eln={"hide": ["value"]})
    value = Quantity(type=MEnum(LICENSES))


class SubjectTerm(ArchiveSection):
    m_def = Section(a_eln={"hide": ["value"]})
    value = Quantity(type=MEnum(SUBJECTS))


class KeywordTerm(ArchiveSection):
    m_def = Section(a_eln={"hide": ["value"]})
    value = Quantity(type=str)


class TrainingResourceRelation(ArchiveSection):
    m_def = Section(
        label_quantity="relation_type",
        description=(
            "Add a relationship to another TrainingResource.\n\n"
            "Tip: Use the pen to select an existing resource. "
            "Or paste a URL into Target identifier and click Save to auto-resolve."
        ),
        a_display={
            "order": [
                "relation_type",
                "target_resource",
                "target_identifier",
                "resolution_status",
                "resolution_message",
            ],
            "editable": {"exclude": ["resolution_status", "resolution_message"]},
        },
    )

    relation_type = Quantity(
        type=MEnum(RELATION_TYPES),
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
        description="Select the type of relationship.",
    )

    target_resource = Quantity(
        type="TrainingResource",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
            showSectionLabel=True,
        ),
        description="Select the target TrainingResource using the pen icon.",
    )

    target_identifier = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.URLEditQuantity),
        description=(
            "Optional alternative to the pen: paste the identifier URL of an existing "
            "TrainingResource here, then click Save. NOMAD will try to resolve it."
        ),
    )

    resolution_status = Quantity(
        type=MEnum(RELATION_STATUS),
        description="Auto-filled on Save: shows what happened during resolution.",
    )

    resolution_message = Quantity(
        type=str,
        description="Auto-filled on Save: details about resolution result.",
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        super().normalize(archive, logger)

        if self.target_resource is not None:
            self.resolution_status = "manual_reference"
            self.resolution_message = "Target resource selected manually."
            return

        target_id = _canonicalize_identifier(self.target_identifier) or ""
        if not target_id:
            self.resolution_status = "identifier_missing"
            self.resolution_message = (
                "No target selected yet. Use the pen or paste an identifier URL and Save."
            )
            return

        from nomad.datamodel.context import ClientContext

        if isinstance(archive.m_context, ClientContext):
            self.resolution_status = "skipped_client_context"
            self.resolution_message = (
                "Auto-resolution runs during server-side processing. Click Save and "
                "check the entry again after processing."
            )
            return

        try:
            from nomad.search import MetadataPagination, search

            schema_qn = "nomad_training_resources.schema_packages.schema_package.TrainingResource"
            query = {f"data.identifier#{schema_qn}": target_id}

            max_candidates = 20
            result = search(
                owner="visible",
                query=query,
                pagination=MetadataPagination(page_size=max_candidates),
                user_id=getattr(archive.metadata.main_author, "user_id", None),
            )

            total = getattr(result.pagination, "total", 0) or 0
            if total == 0:
                self.resolution_status = "identifier_not_found"
                self.resolution_message = (
                    "No TrainingResource found with that identifier URL. "
                    "Either create the missing resource entry, or use the pen to select an entry."
                )
                return

            if total > 1:
                candidates = []
                lines = []
                for hit in (result.data or []):
                    entry_id = hit.get("entry_id")
                    entry_name = hit.get("entry_name")
                    if not entry_name:
                        entry_name = (hit.get("metadata") or {}).get("entry_name")
                    candidates.append({"entry_id": entry_id, "entry_name": entry_name})
                    label = entry_name if entry_name else "<no entry_name>"
                    lines.append(f"- {entry_id}: {label}")

                shown = len(lines)
                suffix = f" (showing {shown} of {total})" if total > shown else ""

                self.resolution_status = "identifier_ambiguous"
                self.resolution_message = (
                    "Multiple TrainingResources found with that identifier URL. "
                    "Please select the correct one with the pen."
                    f"\nMatches{suffix}:\n" + "\n".join(lines)
                )

                logger.warning(
                    "relation_identifier_ambiguous",
                    target_identifier=target_id,
                    total=total,
                    shown=shown,
                    candidates=candidates,
                )
                return

            hit = result.data[0]
            upload_id = hit["upload_id"]
            entry_id = hit["entry_id"]

            m_proxy_value = f"../uploads/{upload_id}/archive/{entry_id}#/data"
            self.target_resource = m_proxy_value

            self.resolution_status = "resolved_from_identifier"
            self.resolution_message = f"Resolved identifier to TrainingResource entry_id={entry_id}."

        except Exception as e:
            logger.warning("relation_identifier_resolution_failed", error=str(e))
            self.resolution_status = "error"
            self.resolution_message = f"Resolution failed: {e}"


class TrainingResource(Schema):
    m_def = Section(
        a_eln={
            "hide": [
                "instructional_method_terms",
                "educational_level_terms",
                "learning_resource_type_terms",
                "format_terms",
                "license_terms",
                "subject_terms",
                "keyword_terms",
                "message",
            ]
        }
    )

    entry_name = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
        description="Entry name (synchronized with NOMAD metadata entry_name).",
    )

    identifier = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.URLEditQuantity),
        links=["https://schema.org/identifier"],
    )

    language = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
        default="en",
        links=["https://schema.org/inLanguage"],
    )
    date_created = Quantity(
        type=Datetime,
        a_eln=ELNAnnotation(component=ELNComponentEnum.DateEditQuantity),
        links=["https://schema.org/dateCreated"],
    )
    date_modified = Quantity(
        type=Datetime,
        a_eln=ELNAnnotation(component=ELNComponentEnum.DateEditQuantity),
        links=["https://schema.org/dateModified"],
    )

    instructional_method = Quantity(
        type=MEnum(INSTRUCTIONAL_METHODS),
        shape=["*"],
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
        links=["http://purl.org/dc/terms/instructionalMethod"],
        description="Select one or more instructional methods.",
    )
    educational_level = Quantity(
        type=MEnum(EDUCATIONAL_LEVELS),
        shape=["*"],
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
        links=["https://schema.org/educationalLevel"],
        description="Select one or more educational levels.",
    )
    learning_resource_type = Quantity(
        type=MEnum(LEARNING_RESOURCE_TYPES),
        shape=["*"],
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
        links=["https://schema.org/learningResourceType"],
        description="Select one or more resource types.",
    )
    format = Quantity(
        type=MEnum(FORMATS),
        shape=["*"],
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
        links=["https://schema.org/encodingFormat"],
        description="Select one or more formats.",
    )
    license = Quantity(
        type=MEnum(LICENSES),
        shape=["*"],
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
        links=["https://schema.org/license"],
        description="Select one or more licenses.",
    )
    subject = Quantity(
        type=MEnum(SUBJECTS),
        shape=["*"],
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
        links=["https://purl.org/dc/terms/subject"],
        description="Select one or more subjects.",
    )
    keyword = Quantity(
        type=str,
        shape=["*"],
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
        links=["https://schema.org/keywords"],
        description="Add one or more keywords.",
    )

    tags = Quantity(
        type=str,
        shape=["*"],
        description="Add a tag that can be used for search.",
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )

    title = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
        links=["https://schema.org/name"],
    )
    description = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.RichTextEditQuantity),
        links=["https://schema.org/description"],
    )

    instructional_method_terms = SubSection(section_def=InstructionalMethodTerm, repeats=True)
    educational_level_terms = SubSection(section_def=EducationalLevelTerm, repeats=True)
    learning_resource_type_terms = SubSection(section_def=LearningResourceTypeTerm, repeats=True)
    format_terms = SubSection(section_def=FormatTerm, repeats=True)
    license_terms = SubSection(section_def=LicenseTerm, repeats=True)
    subject_terms = SubSection(section_def=SubjectTerm, repeats=True)
    keyword_terms = SubSection(section_def=KeywordTerm, repeats=True)

    relations = SubSection(
        section_def=TrainingResourceRelation,
        repeats=True,
        description="Add one or more relationships to other TrainingResource entries.",
    )

    message = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )

    def _sync_terms(self) -> None:
        self.instructional_method_terms = [
            InstructionalMethodTerm(value=v) for v in _unique_clean(self.instructional_method)
        ]
        self.educational_level_terms = [
            EducationalLevelTerm(value=v) for v in _unique_clean(self.educational_level)
        ]
        self.learning_resource_type_terms = [
            LearningResourceTypeTerm(value=v) for v in _unique_clean(self.learning_resource_type)
        ]
        self.format_terms = [FormatTerm(value=v) for v in _unique_clean(self.format)]
        self.license_terms = [LicenseTerm(value=v) for v in _unique_clean(self.license)]
        self.subject_terms = [SubjectTerm(value=v) for v in _unique_clean(self.subject)]
        self.keyword_terms = [KeywordTerm(value=v) for v in _unique_clean(self.keyword)]

    def _sync_entry_name(self, archive: "EntryArchive") -> None:
        if not getattr(archive, "metadata", None):
            return
        if archive.data != self:
            return

        if self.entry_name:
            archive.metadata.entry_name = self.entry_name
        elif self.entry_name is None and archive.metadata.entry_name:
            self.entry_name = archive.metadata.entry_name.split(".")[0].replace("_", " ")

    def _has_meaningful_content_for_defaulting(self) -> bool:
        if isinstance(self.identifier, str) and self.identifier.strip():
            return True
        if isinstance(self.entry_name, str) and self.entry_name.strip():
            return True
        if isinstance(self.title, str) and self.title.strip():
            return True
        if isinstance(self.description, str) and self.description.strip():
            return True
        if _unique_clean(self.keyword):
            return True
        if _unique_clean(self.tags):
            return True
        if self.relations:
            return True
        return False

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        super().normalize(archive, logger)

        self._sync_entry_name(archive)

        self.identifier = _canonicalize_identifier(self.identifier)

        self.tags = _unique_clean(getattr(self, "tags", None))
        if self.tags:
            if not archive.results:
                archive.results = Results(eln=ELN())
            if not archive.results.eln:
                archive.results.eln = ELN()
            existing = _unique_clean(getattr(archive.results.eln, "tags", None))
            for t in self.tags:
                if t not in existing:
                    existing.append(t)
            archive.results.eln.tags = existing

        from nomad.datamodel.context import ClientContext

        fill_defaults = (not isinstance(archive.m_context, ClientContext)) and self._has_meaningful_content_for_defaulting()

        if fill_defaults:
            self.instructional_method = _normalize_enum_list(self.instructional_method)
            self.educational_level = _normalize_enum_list(self.educational_level)
            self.learning_resource_type = _normalize_enum_list(self.learning_resource_type)
            self.format = _normalize_enum_list(self.format)
            self.license = _normalize_enum_list(self.license)
            self.subject = _normalize_enum_list(self.subject)
        else:
            self.instructional_method = _normalize_enum_list_client(self.instructional_method)
            self.educational_level = _normalize_enum_list_client(self.educational_level)
            self.learning_resource_type = _normalize_enum_list_client(self.learning_resource_type)
            self.format = _normalize_enum_list_client(self.format)
            self.license = _normalize_enum_list_client(self.license)
            self.subject = _normalize_enum_list_client(self.subject)

        self.keyword = _normalize_free_list(self.keyword)

        self._sync_terms()

        if self.relations:
            for rel in self.relations:
                try:
                    rel.normalize(archive, logger)
                except Exception as e:
                    logger.warning("relation_normalize_failed", error=str(e))

        logger.info(
            "TrainingResource.normalize",
            parameter=getattr(configuration, "parameter", None),
        )
        self.message = f"Indexed {len(self.keyword_terms)} keywords."


m_package.__init_metainfo__()