from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad.config import config
from nomad.datamodel.data import Schema
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.datamodel.metainfo.basesections import EntityReference
from nomad.metainfo import Datetime, MEnum, Quantity, SchemaPackage
from nomad.metainfo.metainfo import Section, SubSection

configuration = config.get_plugin_entry_point(
    'nomad_training_resources.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()


class Relations(EntityReference):
    """
    Represents the relationships between training resources.
    """

    m_def = Section(a_eln={'hide': ['lab_id', 'name', 'reference']})
    sameAs = Quantity(
        type='TrainingResource',
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
        links=['http://schema.org/sameAs'],
    )
    isPartOf = Quantity(
        type='TrainingResource',
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
        links=['http://purl.org/dc/terms/isPartOf'],
    )
    hasPart = Quantity(
        type='TrainingResource',
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
        links=['http://purl.org/dc/terms/hasPart'],
    )
    isFormatOf = Quantity(
        type='TrainingResource',
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
        links=['http://purl.org/dc/terms/isFormatOf'],
    )
    hasFormat = Quantity(
        type='TrainingResource',
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
        links=['http://purl.org/dc/terms/hasFormat'],
    )
    isReplacedBy = Quantity(
        type='TrainingResource',
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
        links=['http://purl.org/dc/terms/isReplacedBy'],
    )
    replaces = Quantity(
        type='TrainingResource',
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
        links=['http://purl.org/dc/terms/replaces'],
    )
    isReferencedBy = Quantity(
        type='TrainingResource',
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
        links=['http://purl.org/dc/terms/isReferencedBy'],
    )
    references = Quantity(
        type='TrainingResource',
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
        links=['http://purl.org/dc/terms/references'],
    )
    isBasedOn = Quantity(
        type='TrainingResource',
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
        links=['http://schema.org/isBasedOn'],
    )


class TrainingResource(Schema):
    m_def = Section(a_eln={'hide': ['name']})

    name = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
        description='Hidden: automatically set from identifier, so that entries are unique',
    )
    identifier = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.URLEditQuantity),
        links=['https://schema.org/identifier'],
    )
    language = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
        default='en',
        links=['https://schema.org/inLanguage'],
    )
    date_created = Quantity(
        type=Datetime,
        a_eln=ELNAnnotation(component=ELNComponentEnum.DateEditQuantity),
        links=['https://schema.org/dateCreated'],
    )
    date_modified = Quantity(
        type=Datetime,
        a_eln=ELNAnnotation(component=ELNComponentEnum.DateEditQuantity),
        links=['https://schema.org/dateModified'],
    )
    instructional_method = Quantity(
        type=MEnum(['Tutorial', 'HowTo', 'Explanation', 'Reference', 'Undefined']),
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
        links=['http://purl.org/dc/terms/instructionalMethod'],
        description='Single instructional method used for search/filtering.'
    )
    educational_level = Quantity(
        type=MEnum(['Beginner', 'Intermediate', 'Advanced', 'Undefined']),
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
        links=['https://schema.org/educationalLevel'],
        description='Single educational level used for search/filtering.',
    )
    learning_resource_type = Quantity(
        type=MEnum(
            ['FAIRmatTutorial', 'NOMADDocumentation', 'GitRepo', 'NOMADExamples', 'SelfLearning', 'Undefined']
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.RadioEnumEditQuantity),
        links=['https://schema.org/learningResourceType'],
        description='Learning resource type used for search/filtering (with Undefined for missing).',
    )
    format = Quantity(
        type=MEnum(
            [
                'Video File',
                'Technical Article',
                'Presentation Document',
                'Software Application',
                'Source Code',
                'Undefined'
            ]
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.RadioEnumEditQuantity),
        links=['https://schema.org/encodingFormat'],
        description='Format used for search/filtering (with Undefined for missing).',

    )
    license = Quantity(
        type=MEnum(['CC0', 'CC BY', 'MIT License', 'Apache License 2.0', 'GNU GPLv3', 'Undefined']),
        a_eln=ELNAnnotation(component=ELNComponentEnum.RadioEnumEditQuantity),
        links=['https://schema.org/license'],
        description='License used for search/filtering (with Undefined for missing).',
    )
    title = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
        links=['https://schema.org/name'],
    )
    description = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.RichTextEditQuantity),
        links=['https://schema.org/description'],
    )
    subject = Quantity(
        type=MEnum(
            [
                'General NOMAD',
                'Publish',
                'Explore',
                'Analyze',
                'ELN',
                'API',
                'Oasis Customization',
                'Oasis Installation',
                'Oasis Configuration',
                'NOMAD Plugins',
                'Develop NOMAD',
                'NeXus',
                'General RDM',
                'Scientific Use Cases',
                'CAMELS',
                'NOMAD CAMELS',
                'NOMAD Encyclopedia',
                'AI',
                'Undefined',

            ]
        ),
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
        links=['https://purl.org/dc/terms/subject'],
        description='Single subject value used for search/filtering.',
    )

    keywords = Quantity(
        type=str,
        shape=['*'],
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
        links=['https://schema.org/keywords'],
        description='Single keyword used for search/filtering.'
    )

    relations = SubSection(
        section_def=Relations,
        description='Links to related training resources and versions.',
        repeats=False,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        logger.info('NewSchema.normalize', parameter=configuration.parameter)
        self.message = f'Hello {self.name}!'


m_package.__init_metainfo__()
