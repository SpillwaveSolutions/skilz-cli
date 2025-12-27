# Skilz CLI - Technical Documentation

Comprehensive technical documentation for the Skilz CLI project, the universal package manager for AI skills.

**Browse skills:** [skillzwave.ai](https://skillzwave.ai) — The largest agent and agent skills marketplace
**Built by:** [Spillwave](https://spillwave.com) — Leaders in agentic software development

> **📋 Documentation Status:** This documentation is current through **Phase 5** (Image Generation) of the 6-phase documentation workflow. Phase 6 (Validation) is in progress. All diagrams have been converted to images and the core documentation is complete.

## Project Statistics

| Metric | Value |
|--------|-------|
| Source Files | 23 Python modules |
| Source Lines | 2,036+ lines |
| Test Files | 18 test modules |
| Test Cases | 448 tests |
| Test Coverage | 85%+ |
| Python Version | 3.10+ |
| Current Version | 1.2.0 |
| PyPI | [pip install skilz](https://pypi.org/project/skilz/) |

## Documentation Structure

### 00. Overview
- [Project Overview](00_overview/01_project_overview.md) - High-level project description and goals
- [Architecture Overview](00_overview/02_architecture_overview.md) - System architecture and design patterns
- [Installation Guide](00_overview/03_installation.md) - Setup and installation instructions
- [Quick Start](00_overview/04_quick_start.md) - Getting started guide

### 01. Architecture
- [System Architecture](01_architecture/01_system_architecture.md) - Overall system design
- [Module Hierarchy](01_architecture/02_module_hierarchy.md) - Package and module organization
- [Data Flow](01_architecture/03_data_flow.md) - How data flows through the system
- [Design Patterns](01_architecture/04_design_patterns.md) - Architectural patterns used

### 02. Core Modules
- [CLI Module](02_core_modules/01_cli.md) - Command-line interface and argument parsing
- [Installer Module](02_core_modules/02_installer.md) - Core installation orchestration
- [Registry Module](02_core_modules/03_registry.md) - Registry loading and skill resolution
- [Scanner Module](02_core_modules/04_scanner.md) - Installed skill scanning
- [Git Operations](02_core_modules/05_git_ops.md) - Git repository management
- [Agents Module](02_core_modules/06_agents.md) - Agent detection and path resolution
- [Manifest Module](02_core_modules/07_manifest.md) - Manifest file handling
- [Errors Module](02_core_modules/08_errors.md) - Custom exception hierarchy

### 03. Commands
- [Install Command](03_commands/01_install_cmd.md) - skill installation implementation
- [List Command](03_commands/02_list_cmd.md) - List installed skills
- [Update Command](03_commands/03_update_cmd.md) - Update skills to registry versions
- [Remove Command](03_commands/04_remove_cmd.md) - Uninstall skills

### 04. Workflows
- [Installation Workflow](04_workflows/01_installation_workflow.md) - Step-by-step installation process
- [Update Workflow](04_workflows/02_update_workflow.md) - Update detection and execution
- [Registry Resolution](04_workflows/03_registry_resolution.md) - How skills are resolved
- [Manifest Management](04_workflows/04_manifest_management.md) - Manifest lifecycle

### 05. Testing
- [Test Architecture](05_testing/01_test_architecture.md) - Testing strategy and structure
- [Test Coverage](05_testing/02_test_coverage.md) - Coverage reports and gaps
- [Running Tests](05_testing/03_running_tests.md) - How to run the test suite

### 99. Appendices
- [API Reference](99_appendices/01_api_reference.md) - Complete API documentation
- [Configuration Reference](99_appendices/02_configuration.md) - Registry format and manifest schema
- [Troubleshooting](99_appendices/03_troubleshooting.md) - Common issues and solutions
- [Development Guide](99_appendices/04_development.md) - Contributing and development workflow
- [Glossary](99_appendices/05_glossary.md) - Terms and definitions

## Diagrams

All diagrams are available in both Mermaid/PlantUML source and rendered image formats:

- [diagrams/mermaid/](diagrams/mermaid/) - Mermaid diagram sources
- [diagrams/plantuml/](diagrams/plantuml/) - PlantUML diagram sources
- [diagrams/images/](diagrams/images/) - Rendered PNG/SVG images

### Key Diagrams

1. **Architecture Diagram** - System component overview
2. **Installation Sequence** - Installation workflow
3. **Class Diagrams** - Core module class structures
4. **Data Flow Diagrams** - Registry resolution and skill installation
5. **State Diagrams** - Skill lifecycle states

## Quick Navigation

### For New Contributors
1. Start with [Project Overview](00_overview/01_project_overview.md)
2. Review [Architecture Overview](00_overview/02_architecture_overview.md)
3. Read [Development Guide](99_appendices/04_development.md)
4. Study [Test Architecture](05_testing/01_test_architecture.md)

### For Users
1. Begin with [Installation Guide](00_overview/03_installation.md)
2. Follow [Quick Start](00_overview/04_quick_start.md)
3. Reference [CLI Commands](03_commands/) as needed
4. Check [Troubleshooting](99_appendices/03_troubleshooting.md) if issues arise

### For Maintainers
1. Review [System Architecture](01_architecture/01_system_architecture.md)
2. Understand [Module Hierarchy](01_architecture/02_module_hierarchy.md)
3. Study [Core Modules](02_core_modules/) documentation
4. Check [Test Coverage](05_testing/02_test_coverage.md)

## Documentation Standards

This documentation follows these principles:

- **Exhaustive Coverage** - Every module, class, function, and workflow is documented
- **Code Examples** - Real examples from the codebase
- **Diagrams** - Visual representation of complex concepts
- **Cross-References** - Links between related topics
- **Type Annotations** - All signatures include type information
- **Error Handling** - Exception flows are documented

## Building This Documentation

The documentation was generated using the tech-doc-generator skill with the following parameters:

```bash
project_dir: /Users/richardhightower/clients/spillwave/src/skilz-cli
output_dir: docs/initial
```

Generation date: 2025-12-14

## License

This documentation is part of the Skilz CLI project and is licensed under the MIT License.

## See Also

- [Main README](../../README.md) - Project README
- [User Manual](../USER_MANUAL.md) - User-focused documentation
- [SDD Specifications](.speckit/) - Spec-driven development artifacts
