# Implementation Plan: Evolution of Todo

**Branch**: `001-todo-evolution` | **Date**: 2026-01-18 | **Spec**: specs/001-todo-evolution/spec.md
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The Evolution of Todo project implements a progressive transformation of a simple CLI-based todo application into a sophisticated cloud-native AI chatbot across 5 distinct phases. Each phase builds upon the previous one, starting with a Python console app (Phase I) and culminating in a distributed system with Kafka, Dapr, and AI capabilities (Phase V). The implementation follows the constitution's requirements for spec-driven development, AI-native architecture, and iterative evolution with strict adherence to technology stack constraints.

## Technical Context

**Language/Version**: Python 3.13+ (Phase I), Python 3.13+/TypeScript (Phase II-V)
**Primary Dependencies**: cmd2/click (Phase I), FastAPI + SQLModel + Better Auth (Phase II), OpenAI Agents SDK + MCP SDK (Phase III), Docker + Kubernetes + Helm (Phase IV), Kafka + Dapr (Phase V)
**Storage**: In-memory (Phase I), Neon Serverless PostgreSQL (Phase II-V with Dapr state management)
**Testing**: pytest (all phases), with contract testing for API validation
**Target Platform**: Cross-platform (console app), Web browsers (Phase II+), Cloud-native (Phase IV+)
**Project Type**: Multi-phase evolution from single console app to distributed web services
**Performance Goals**: <500ms response time for API calls (Phase II+), support 100 concurrent users (Phase V), 95% success rate for basic operations across all phases
**Constraints**: Follow 5-phase evolution strictly, use mandated tech stacks per phase, maintain backward compatibility where possible, ensure user data isolation (Phase II+)
**Scale/Scope**: Single user (Phase I), multi-user (Phase II+), distributed microservices (Phase V)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Spec-Driven Development Compliance**: ✓ Plan follows SDD workflow (Specify → Plan → Tasks → Implement)
2. **AI-Native and Agentic Focus**: ✓ Plan incorporates OpenAI Agents SDK and MCP SDK in Phase III
3. **Iterative Evolution**: ✓ Plan follows 5-phase evolution with each building on previous
4. **Tech Stack Compliance**: ✓ Plan uses mandated technologies for each phase (Python 3.13+, Next.js 16+, FastAPI, SQLModel, Neon, Better Auth, etc.)
5. **Security First**: ✓ Plan includes authentication from Phase II with JWT and user isolation
6. **Token Efficiency**: ✓ Plan uses modular architecture to promote reusability
7. **No Manual Code**: ✓ Plan assumes all code generation via Claude Code as mandated
8. **User Isolation**: ✓ Plan enforces user data isolation from Phase II onwards
9. **Event-Driven Architecture**: ✓ Plan incorporates Kafka and Dapr for Phase V

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-evolution/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── api-v1.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
hackathon-evolution-todo/
├── .spec-kit/                  # Spec-Kit Plus configuration
│   └── config.yaml
├── specs/                      # All specification artifacts
│   ├── constitution.md
│   └── 001-todo-evolution/    # Current feature specs
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md
│       ├── contracts/
│       │   └── api-v1.yaml
│       └── checklists/
│           └── requirements.md
├── .memory/                    # Optional agent memory if needed
├── CLAUDE.md                   # Root instructions → @AGENTS.md
├── AGENTS.md                   # Strict SDD governance rules
├── src/                        # Phase I: Python CLI app
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── todo.py                 # Task model and service
│   └── cli_commands.py         # Command handlers
├── frontend/                   # Phase II+: Next.js app
│   ├── CLAUDE.md
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   │   ├── page.tsx       # Dashboard
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── components/        # Reusable components
│   │   │   ├── TaskCard.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskList.tsx
│   │   └── lib/               # API client and utilities
│   │       └── api.ts
│   └── tests/
├── backend/                    # Phase II+: FastAPI app
│   ├── CLAUDE.md
│   ├── pyproject.toml         # UV dependencies
│   ├── main.py                # App entry point
│   ├── models/                # SQLModel definitions
│   │   ├── user.py
│   │   └── task.py
│   ├── routes/                # API endpoints
│   │   ├── tasks.py
│   │   ├── auth.py
│   │   └── chat.py (Phase III+)
│   ├── services/              # Business logic
│   │   └── task_service.py
│   ├── db.py                  # Database connection
│   └── tests/
├── mcp-tools/                 # Phase III: MCP server
│   ├── server.py
│   └── tools/
│       ├── add_task.py
│       ├── list_tasks.py
│       ├── complete_task.py
│       ├── delete_task.py
│       └── update_task.py
├── k8s/                       # Phase IV+: Helm charts
│   ├── todo-app/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       └── ingress.yaml
│   └── postgres/
├── docker/                    # Phase IV+: Dockerfiles
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── docker-compose.yml
├── dapr-components/           # Phase V: Dapr configurations
│   ├── kafka-pubsub.yaml
│   ├── postgres-statestore.yaml
│   ├── jobs-component.yaml
│   └── secretstore.yaml
├── scripts/                   # Utility scripts
│   ├── migrate.py
│   ├── seed_data.py
│   └── health_check.py
├── docs/                      # Documentation
│   ├── architecture.md
│   └── deployment.md
└── README.md
```

**Structure Decision**: Multi-phase evolution architecture with separate frontend/backend services following the constitution's monorepo structure requirement. The structure supports the progressive evolution from CLI to distributed cloud services with AI capabilities.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | | No constitution violations identified |
