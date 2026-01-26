<!-- SYNC IMPACT REPORT:
Version change: 1.0.0 → 1.1.0
Modified principles: None (completely new constitution)
Added sections: All sections per user specification
Removed sections: Template placeholders
Templates requiring updates: ✅ .specify/templates/plan-template.md, ✅ .specify/templates/spec-template.md, ✅ .specify/templates/tasks-template.md
Follow-up TODOs: None
-->
# Evolution of Todo Constitution

## Core Principles

### I. Spec-Driven Development as Core Workflow
All implementation must follow the SDD loop: Specify → Plan → Tasks → Implement. No manual coding is allowed; all code generation must originate from Claude Code based on refined specs. Agents must refine specs iteratively until outputs are correct and error-free.

### II. AI-Native and Agentic Focus
The project emphasizes Reusable Intelligence through subagents, agent skills, and blueprints. AI agents (e.g., via OpenAI Agents SDK and MCP SDK) must handle logic, with humans acting as architects.

### III. Iterative Evolution
Build progressively across 5 phases, ensuring each phase builds on the previous without regressions. Phases must be backward-compatible where possible.

### IV. Token Efficiency and Error-Free Design
Specs must be concise, modular, and reusable to minimize token usage in AI prompts. Error handling must be explicit in all components; aim for 100% test coverage in critical paths (e.g., auth, data persistence).

### V. Cloud-Native Mindset
From Phase IV onward, prioritize scalability, resilience, and observability. Use stateless designs, event-driven patterns, and AIOps tools.

### VI. Ethical and Inclusive Development
Support multi-language (e.g., Urdu bonus), accessibility (e.g., voice commands bonus), and user privacy. No data collection without consent; comply with GDPR-like principles.

### VII. Performance Expectations
Response times < 500ms for API calls; scale to 100 concurrent users in Phase V. Optimize for low-resource environments (e.g., Minikube).

### VIII. Security First
Implement authentication from Phase II; use JWT for stateless auth. No hard-coded secrets; use environment variables or secret managers.

### IX. Reusability and Modularity
Create reusable agent skills and cloud-native blueprints for deployment. Favor composition over inheritance; modular monorepo structure.

## Tech Stack Constraints

### Core Tools Across All Phases:
- AI Coding: Claude Code for all code generation.
- Spec Management: Spec-Kit Plus for organizing specs (e.g., /specs folder with subdirs for features, api, database, ui).
- Version Control: GitHub public repo with monorepo structure.

### Phase-Specific Stacks (No deviations allowed):
- Phase I: Python 3.13+, UV for dependencies, in-memory storage. No external services.
- Phase II: Frontend: Next.js 16+ (App Router, TypeScript, Tailwind CSS). Backend: FastAPI, SQLModel. Database: Neon Serverless PostgreSQL. Auth: Better Auth with JWT.
- Phase III: Add OpenAI ChatKit (frontend), OpenAI Agents SDK, Official MCP SDK. Stateless MCP tools for task operations.
- Phase IV: Docker (with Gordon AI if available), Minikube, Helm Charts, kubectl-ai, Kagent for AIOps.
- Phase V: Add Kafka (Redpanda Cloud or Strimzi self-hosted), Dapr for event-driven architecture. Deploy to DigitalOcean Kubernetes (DOKS) or alternatives (Azure AKS, Google GKE, Oracle OKE). CI/CD: GitHub Actions.

### Bonus Features Stack:
Reusable Intelligence (Claude Code subagents), Cloud-Native Blueprints (agent skills), Multi-language (Urdu via NLP libs), Voice Commands (Web Speech API or similar).

### Prohibited Practices:
No pip installs outside UV; no internet access in code execution except via approved APIs (e.g., Polygon, Coingecko). No vendor lock-in; use abstractions like Dapr.

## Architecture Values and Patterns

### Monorepo Structure:
Root with /specs, /frontend, /backend, CLAUDE.md, etc. Use layered CLAUDE.md files for context.

### API Design:
RESTful in Phase II (with user_id in paths); MCP tools in Phase III (stateless, database-backed).

### Data Management:
In-memory (Phase I), Persistent with SQLModel (Phase II+). Event sourcing via Kafka (Phase V).

### State Management:
Stateless servers; persist conversations and tasks in DB.

### Error Handling Patterns:
Use HTTPException in FastAPI; graceful degradation in agents (e.g., confirm actions, handle "task not found").

### Testing and Validation:
Each task must include unit/integration tests. Acceptance criteria must be verifiable.

### Deployment Blueprints:
Use spec-driven blueprints for infrastructure (e.g., Helm charts generated via kubectl-ai).

### Hierarchy of Truth:
Constitution > Specifications > Plans > Tasks. Conflicts resolved by updating higher levels.

## Constraints and Non-Negotiables

### No Manual Code:
Refine specs until Claude Code generates correctly. Review prompts/iterations for judging.

### Feature Progression:
Implement Basic (all phases), Intermediate (Phase V), Advanced (Phase V). Bonus for extra points.

### Authentication and Isolation:
From Phase II, enforce user isolation; no shared data.

### Scalability:
Design for horizontal scaling; use Dapr for loose coupling in Phase V.

### Documentation:
Every repo must have README.md, CLAUDE.md, specs history. Demo videos <90s.

### Amendments:
Changes require spec updates and justification linking back to hackathon requirements.

This constitution ensures a smooth, token-efficient, error-free project. Agents must reference it in all outputs.

## Governance

Constitution supersedes all other practices. All implementation must follow the defined SDD workflow. Amendments require formal spec updates with justification linking back to hackathon requirements. All agents must strictly adhere to these principles; no code, plan, or task can violate these principles without explicit amendment through a spec update process. Compliance is verified through the SDD loop: Specification → Plan → Tasks → Implementation.

**Version**: 1.1.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-01-18