# Project Constitution - AGENTS.md

## Core Principles

### 1. Anti-"Vibe Coding" Policy
- No code shall be written without a corresponding task in `speckit.tasks`
- All implementations must follow the Specify → Plan → Tasks → Implement lifecycle
- Adherence to Spec-Driven Development (SDD) is mandatory

### 2. Technology Stack Requirements
- Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS, Better Auth
- Backend: FastAPI, SQLModel (ORM), Neon Serverless PostgreSQL
- AI/MCP: OpenAI Agents SDK and Official MCP SDK for chatbot interface
- Infrastructure: Kubernetes/Helm, Dapr, Kafka

### 3. Architecture Constraints
- Maintain statelessness in Phase 3+ backend
- Persist all conversation state to database via Dapr or direct DB calls
- Follow clean separation between Phase 1 (console) and Phases 2-5 (full-stack)

### 4. Naming and Structure Conventions
- Phase I (In-Memory Console App) in `/phase-1-console`
- Phases II-V (Full-Stack & Cloud Native) in `/full-stack-app`
- Specifications organized in `/full-stack-app/specs/` subdirectories
- Infrastructure components in `/full-stack-app/infrastructure/`

### 5. Quality Assurance
- All changes must preserve existing functionality
- Backwards compatibility is essential during refactorings
- Automated verification of structure compliance required

## Workflow Enforcement
This constitution explicitly forbids "vibe coding" and mandates the Specify → Plan → Tasks → Implement lifecycle for all development activities.