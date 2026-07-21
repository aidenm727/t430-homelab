"""Public boundary for School Learning v0.1."""

from .core import (
    SchoolLearningError,
    Workspace,
    add_material,
    build_study_brief,
    default_data_root,
    ensure_topic,
    initialize_course,
    iter_sessions,
    load_course,
    load_materials,
    load_topics,
    record_session,
    workspace,
)
from .render import render_course

__all__ = (
    "SchoolLearningError",
    "Workspace",
    "add_material",
    "build_study_brief",
    "default_data_root",
    "ensure_topic",
    "initialize_course",
    "iter_sessions",
    "load_course",
    "load_materials",
    "load_topics",
    "record_session",
    "render_course",
    "workspace",
)
