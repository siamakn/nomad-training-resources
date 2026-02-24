from nomad.config.models.plugins import NormalizerEntryPoint
from pydantic import Field


class NewNormalizerEntryPoint(NormalizerEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad_training_resources.normalizers.normalizer import NewNormalizer

        return NewNormalizer(**self.model_dump())


training_resources_normalizer = NewNormalizerEntryPoint(
    name='training_resources_normalizer',
    description='New normalizer entry point configuration.',
)
