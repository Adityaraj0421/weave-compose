"""MCP server exposing Weave skill selection and composition as tools.

Implements three tools over stdio transport:
  - weave_status: report registry state
  - weave_load: load skills from a directory
  - weave_query: query loaded skills and optionally return composed context

Stdout is reserved for the MCP wire protocol. All diagnostic output
must use the logger — never print() or typer.echo() in this module.
"""

import logging

logger = logging.getLogger(__name__)
