from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class NewSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad_training_resources.schema_packages.schema_package import m_package

        return m_package


training_resources_schema = NewSchemaPackageEntryPoint(
    name='training_resources_schema',
    description='New schema package entry point configuration.',
)