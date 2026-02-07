# ADR-001: Event-Driven Microservices Architecture with Dapr and Kafka

## Status
Accepted

## Date
2026-01-28

## Context
For Phase V of the Cloud-Native AI Todo Platform, we needed to evolve from a monolithic architecture to a production-grade, event-driven microservices system. The system required advanced task management features (priorities, tags, due dates, reminders, recurring tasks) while maintaining scalability, reliability, and resilience. Traditional synchronous communication patterns would create tight coupling and potential bottlenecks, especially for features like recurring tasks and notifications that require asynchronous processing.

## Decision
We will implement an event-driven microservices architecture using:
- **Kafka** as the central event backbone for loose coupling, async processing, auditability, and real-time sync
- **Dapr** as the service mesh for abstracting away direct Kafka access, providing service invocation, pub/sub messaging, mTLS security, and secrets management
- **Four dedicated services**: Main API (orchestration), Recurring Task, Notification, and Audit services
- **Event sourcing** for task operations to maintain system state and enable replay capabilities

## Alternatives Considered
1. **Monolithic architecture with database polling**: Would create tight coupling, performance issues, and difficulty scaling individual components
2. **Direct database sharing between services**: Would violate microservices principles and create data consistency challenges
3. **Simple REST API communication**: Would create synchronous dependencies and potential cascade failures
4. **Message queues without service mesh**: Would require direct infrastructure management and lack the security and observability benefits of Dapr

## Consequences
### Positive
- High scalability through horizontal service scaling
- Loose coupling enabling independent service development and deployment
- Improved resilience through asynchronous, fault-tolerant event processing
- Better separation of concerns with dedicated services for specific responsibilities
- Enhanced auditability through immutable event logs
- Simplified security through Dapr's mTLS and secrets management
- Future extensibility for additional services and features

### Negative
- Increased complexity in debugging and distributed tracing
- Additional infrastructure requirements (Kafka, Dapr sidecars)
- Potential for eventual consistency between services
- Learning curve for Dapr and event-driven patterns
- Higher operational overhead compared to monolithic approach

## Implementation Notes
- All services are stateless and horizontally scalable
- Events include correlation IDs and versioning for traceability
- Consumers implement idempotent processing to handle at-least-once delivery
- Dapr pub/sub abstraction allows Kafka to be swapped without code changes
- All secrets accessed only through Dapr Secrets API