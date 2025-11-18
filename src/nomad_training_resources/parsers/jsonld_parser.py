from typing import (
    TYPE_CHECKING, Dict,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )
from nomad.config import config
from nomad.datamodel.metainfo.workflow import Workflow
from nomad.parsing.parser import ElnMatchingParser
from ..schema_packages.schema_package import TrainingResource

# configuration = config.get_plugin_entry_point(
#     'nomad_training_resources.parsers:parser_entry_point'
# )

import logging  # add this import

def _log_info(logger, event, **kv):
    try:
        logger.info(event, **kv)            # structlog style
    except TypeError:
        # stdlib logging fallback
        logger.info('%s %s', event, kv if kv else '')

def _log_exc(logger, event, **kv):
    try:
        logger.exception(event, **kv)       # structlog style
    except TypeError:
        logger.exception('%s %s', event, kv if kv else '')

def _as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]

# allowed values from your schema
_ALLOWED_INSTR = {"Tutorial", "HowTo", "Explanation", "Reference", "Undefined"}
_ALLOWED_LEVEL = {"Beginner", "Intermediate", "Advanced", "Undefined"}
_ALLOWED_LRT   = {"FAIRmatTutorial", "NOMADDocumentation", "GitRepo", "NOMADExamples", "SelfLearning", "Undefined"}
_ALLOWED_FMT   = {"Video File", "Technical Article", "Presentation Document", "Software Application", "Source Code", "Undefined"}
_ALLOWED_LIC   = {"CC0", "CC BY", "MIT License", "Apache License 2.0", "GNU GPLv3", "Undefined"}
_ALLOWED_SUBJ  = {
    "General NOMAD","Publish","Explore","Analyze","ELN","API",
    "Oasis Customization","Oasis Installation","Oasis Configuration",
    "NOMAD Plugins","Develop NOMAD","Scientific Use Cases",
    "NeXus","General RDM","CAMELS","NOMAD CAMELS","NOMAD Encyclopedia","AI", "Undefined"
}

# simple alias maps for common inputs
_MAP_LIC = {
    "https://creativecommons.org/publicdomain/zero/1.0/": "CC0",
    "cc0": "CC0",
    "https://creativecommons.org/licenses/by/4.0/": "CC BY",
    "cc by": "CC BY",
    "mit": "MIT License",
    "mit license": "MIT License",
    "apache 2.0": "Apache License 2.0",
    "apache-2.0": "Apache License 2.0",
    "gplv3": "GNU GPLv3",
    "gpl-3.0": "GNU GPLv3",
}
_MAP_FMT = {
    "video": "Video File", "videofile": "Video File", "schema:videoobject": "Video File",
    "article": "Technical Article", "technicalarticle": "Technical Article",
    "presentation": "Presentation Document", "slides": "Presentation Document",
    "softwareapplication": "Software Application", "app": "Software Application",
    "sourcecode": "Source Code", "code": "Source Code",
}
_MAP_LRT = {
    "fairmattutorial": "FAIRmatTutorial",
    "nomaddocumentation": "NOMADDocumentation",
    "gitrepo": "GitRepo",
    "nomadexamples": "NOMADExamples",
}

def _map_enum(val_or_vals, allowed: set[str], aliases: dict[str, str]):
    if val_or_vals is None:
        return None
    out = []
    for v in _as_list(val_or_vals):
        s = str(v).strip()
        if s in allowed:
            out.append(s); continue
        key = s.lower().replace(" ", "").replace("_", "")
        m = aliases.get(key)
        if m and m in allowed:
            out.append(m)
    return out or None





class TrainingJSONLDParser(ElnMatchingParser):
    """
    Minimal step-1 parser: rely on ElnMatchingParser to create archive.data
    (instance of TrainingResource because eln_m_def is set in the entry point).
    """
    def parse(
            self,
            mainfile: str,
            archive: 'EntryArchive',
            logger: 'BoundLogger' = None,
            child_archives: Dict[str, 'EntryArchive'] | None = None,
    ) -> None:
        import json
        from pathlib import Path

        print("parser is called")

        # 1) DO NOT call super().parse(...) while developing:
        #    it would set archive.data to ElnParserRawFile.
        # super().parse(mainfile, archive, logger=logger, child_archives=child_archives)

        # 2) Ensure we are populating your schema section
        tr = TrainingResource()
        archive.data = tr

        # 3) Load one JSON object (json/jsonld or first line of jsonl)
        obj = None
        try:
            with archive.m_context.raw_file(mainfile, 'r') as f:
                if mainfile.lower().endswith('.jsonl'):
                    line = f.readline()
                    obj = json.loads(line) if line else {}
                else:
                    obj = json.load(f)
        except Exception:
            p = Path(mainfile)
            with p.open('r', encoding='utf-8') as f:
                if p.suffix == '.jsonl':
                    line = f.readline()
                    obj = json.loads(line) if line else {}
                else:
                    obj = json.load(f)
        if isinstance(obj, list):
            obj = obj[0] if obj else {}

        # 4) Map core fields (your existing mapping, unchanged)
        def get(*keys, default=None):
            for k in keys:
                if k in obj and obj[k] not in (None, ''):
                    return obj[k]
            return default

        tr.identifier = get('@id', 'schema:identifier', 'identifier')
        tr.title = get('schema:name', 'dct:title', 'title')
        tr.description = get('schema:description', 'dct:description', 'description')
        tr.language = get('schema:inLanguage', 'language', default='en')
        if isinstance(tr.title, str):
            tr.title = tr.title.strip()
        if isinstance(tr.description, str):
            tr.description = tr.description.strip()
        if tr.language:
            tr.language = str(tr.language).strip() or 'en'
        else:
            tr.language = 'en'

        tr.date_created = get('schema:dateCreated', 'dateCreated')
        tr.date_modified = get('schema:dateModified', 'dateModified')

        kw = get('schema:keywords', 'keywords', default=[])
        if isinstance(kw, str):
            kw = [p.strip() for p in kw.split(',') if p.strip()]
        elif not isinstance(kw, list):
            kw = []
        tr.keywords = kw

        subs = []
        for v in _as_list(get('dct:subject', 'subject')):
            s = str(v).strip()
            if s in _ALLOWED_SUBJ:
                subs.append(s)
            elif logger:
                logger.info('Skipping non-allowed subject', subject=s)
        tr.subject = subs or None

        if not getattr(tr, 'name', None):
            tr.name = tr.identifier or tr.title

        # ---- ENUMS ----
        tr.instructional_method = _map_enum(
            get('dct:instructionalMethod', 'instructionalMethod'),
            _ALLOWED_INSTR, {}
        )

        tr.educational_level = _map_enum(
            get('schema:educationalLevel', 'educationalLevel'),
            _ALLOWED_LEVEL, {}
        )

        _lrt = _map_enum(
            get('schema:learningResourceType', 'learningResourceType'),
            _ALLOWED_LRT, _MAP_LRT
        )
        # scalar in your schema → pick first if present
        tr.learning_resource_type = _lrt[0] if _lrt else None

        _fmt = _map_enum(
            get('schema:encodingFormat', 'format'),
            _ALLOWED_FMT, _MAP_FMT
        )
        tr.format = _fmt[0] if _fmt else None

        lic = get('schema:license', 'license')
        if isinstance(lic, list):
            lic = lic[0] if lic else None
        if isinstance(lic, str):
            lk = lic.lower().strip()
            lic = _MAP_LIC.get(lk, lic)
        tr.license = lic if lic in _ALLOWED_LIC else None

        # Friendly entry name shown in GUI/search
        try:
            title = (tr.title or '').strip()
            archive.metadata.entry_name = title or tr.identifier or 'Training resource'
        except Exception:
            pass

