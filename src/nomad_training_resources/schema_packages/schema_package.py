from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad.config import config
from nomad.datamodel.data import ArchiveSection, Schema
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.metainfo import Datetime, MEnum, Quantity, SchemaPackage, Section, SubSection

configuration = config.get_plugin_entry_point(
    "nomad_training_resources.schema_packages:schema_package_entry_point"
)

m_package = SchemaPackage()

# -----------------------------------------------------------------------------
# Controlled vocabularies (re-used for both the user-facing lists and the hidden
# index subsections)
# -----------------------------------------------------------------------------

INSTRUCTIONAL_METHODS = ["Tutorial", "HowTo", "Explanation", "Reference", "Undefined"]
EDUCATIONAL_LEVELS = ["Beginner", "Intermediate", "Advanced", "Undefined"]
LEARNING_RESOURCE_TYPES = [
    "FAIRmatTutorial",
    "NOMADDocumentation",
    "GitRepo",
    "NOMADExamples",
    "SelfLearning",
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


def _unique_clean(values: Optional[Iterable[str]]) -> List[str]:
    """De-dup, strip, drop empty/None; keep order."""
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


# -----------------------------------------------------------------------------
# Hidden "terms" subsections used for indexing / aggregations in Apps.
# Each element is scalar => NOMAD search indexing behaves like repeated subsections.
# -----------------------------------------------------------------------------

class InstructionalMethodTerm(ArchiveSection):
    m_def = Section()
    value = Quantity(type=MEnum(INSTRUCTIONAL_METHODS))


class EducationalLevelTerm(ArchiveSection):
    m_def = Section()
    value = Quantity(type=MEnum(EDUCATIONAL_LEVELS))


class LearningResourceTypeTerm(ArchiveSection):
    m_def = Section()
    value = Quantity(type=MEnum(LEARNING_RESOURCE_TYPES))


class FormatTerm(ArchiveSection):
    m_def = Section()
    value = Quantity(type=MEnum(FORMATS))


class LicenseTerm(ArchiveSection):
    m_def = Section()
    value = Quantity(type=MEnum(LICENSES))


class SubjectTerm(ArchiveSection):
    m_def = Section()
    value = Quantity(type=MEnum(SUBJECTS))


class KeywordTerm(ArchiveSection):
    m_def = Section()
    value = Quantity(type=str)


# -----------------------------------------------------------------------------
# Main schema
# -----------------------------------------------------------------------------

class TrainingResource(Schema):
    m_def = Section(
        a_eln={
            "hide": [
                "name",
                # hide the indexing mirrors (they still exist + get indexed)
                "instructional_method_terms",
                "educational_level_terms",
                "learning_resource_type_terms",
                "format_terms",
                "license_terms",
                "subject_terms",
                "keyword_terms",
                # optional debug/info
                "message",
            ]
        }
    )

    # --- Internal/identifier-ish ---
    name = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
        description="Hidden: automatically set from identifier, so that entries are unique",
    )
    identifier = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.URLEditQuantity),
        links=["https://schema.org/identifier"],
    )

    # --- Simple metadata ---
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

    # --- Multi-value (user-facing) quantities ---
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

    # --- Descriptive content ---
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

    # --- Hidden “index mirror” subsections (repeating) ---
    instructional_method_terms = SubSection(section_def=InstructionalMethodTerm, repeats=True)
    educational_level_terms = SubSection(section_def=EducationalLevelTerm, repeats=True)
    learning_resource_type_terms = SubSection(section_def=LearningResourceTypeTerm, repeats=True)
    format_terms = SubSection(section_def=FormatTerm, repeats=True)
    license_terms = SubSection(section_def=LicenseTerm, repeats=True)
    subject_terms = SubSection(section_def=SubjectTerm, repeats=True)
    keyword_terms = SubSection(section_def=KeywordTerm, repeats=True)

    # Optional debug/info
    message = Quantity(type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity))

    def _sync_terms(self) -> None:
        """Mirror list-quantities into repeated subsections for search indexing."""
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

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        super().normalize(archive, logger)

        if self.identifier:
            self.name = self.identifier

        self._sync_terms()

        logger.info("TrainingResource.normalize", parameter=getattr(configuration, "parameter", None))
        self.message = f"Indexed {len(self.keyword_terms)} keywords."


m_package.__init_metainfo__()
