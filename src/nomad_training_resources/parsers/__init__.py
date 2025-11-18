from nomad.config.models.plugins import ElnParserEntryPoint
from pydantic import Field


class TrainingJSONLDEPN(ElnParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from .jsonld_parser import TrainingJSONLDParser
        return TrainingJSONLDParser(**self.model_dump())

training_jsonld_parser = TrainingJSONLDEPN(
    name='training_jsonld_parser',
    description='Parse RDF/JSON-LD (or JSONL) into TrainingResource ELN entries.',
    # ---- matching: filenames we care about
    mainfile_name_re=r'.*\.(jsonld|jsonl|json)$',
    # quick content probe: look for "@context" somewhere near the start
    mainfile_contents_re=r'"@context"\s*:',
    # tell the ELN entry point which section to create as archive.data
    eln_m_def='nomad_training_resources.schema_packages.schema_package.TrainingResource',
    # keep the raw-file helper section (default is fine)
    raw_file_m_def='nomad.datamodel.metainfo.eln.ElnParserRawFile',
    # for now we keep update=False; can enable later
    update=False,
)
