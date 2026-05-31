"""Pydantic model for the DeepChart canonical instance schema (v1).

Mirrors schema/instance.schema.json. Import this in the Phase 3 ETL to build
and validate records, and in eval/ to load them.

    from schema.instance_model import Instance
    inst = Instance.model_validate_json(line)   # one jsonl line
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class Domain(str, Enum):
    academic = "academic"
    finance = "finance"
    research_report = "research_report"


class SourceType(str, Enum):
    nature = "nature"
    annual_report = "annual_report"
    cbinsights = "cbinsights"
    startupblink = "startupblink"
    startupgenome = "startupgenome"


class Level(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class CodeType(str, Enum):
    python = "python"
    html = "html"


class Modality(str, Enum):
    text = "text"
    multimodal = "multimodal"


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Source(_Base):
    type: SourceType
    doc_id: str
    url: str = ""
    fig: str = ""
    notes: str = ""


class Info(_Base):
    # text domains (academic/finance) always populate level+chart_type;
    # research_report does not pre-declare them -> both optional.
    level: Level | None = None
    chart_type: str = ""
    chart_type_subclass: str = ""
    topic_domain: list[str] = []
    chart_description: dict[str, Any] | None = None


class Query(_Base):
    template: str
    code_types: list[CodeType]
    metadata: dict[str, Any] | None = None

    @field_validator("code_types")
    @classmethod
    def _non_empty(cls, v: list[CodeType]) -> list[CodeType]:
        if not v:
            raise ValueError("code_types must list at least one renderer")
        return v


class ContextVariants(_Base):
    normal: list[str]
    long: list[str] | None = None
    ultra_long: list[str] | None = None

    @field_validator("normal")
    @classmethod
    def _normal_non_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("context.variants.normal must be non-empty")
        return v


class Context(_Base):
    modality: Modality
    variants: ContextVariants


class Program(_Base):
    stage1_extract: str | None = None
    stage2_python: str | None = None
    stage2_html: str | None = None


class References(_Base):
    d_src: str
    d_der: str | None = None
    program: Program
    chart_image: str = ""  # "" => render on the fly from program.stage2_*


class Instance(_Base):
    uid: str
    domain: Domain
    orig_id: str
    source: Source
    info: Info
    query: Query
    context: Context
    references: References

    @field_validator("uid")
    @classmethod
    def _uid_shape(cls, v: str) -> str:
        if "/" not in v:
            raise ValueError("uid must be '<domain>/<orig_id>'")
        return v
