# Backup and Disaster Recovery Procedures

## Overview

This document outlines the backup and disaster recovery procedures for the Cloud-Native AI Todo Platform. It covers data backup strategies, recovery procedures, and business continuity planning.

## Data Backup Strategy

### 1. Database Backups (PostgreSQL)

#### Automated Backups
- **Frequency**: Daily at 2:00 AM UTC
- **Retention**: 30 days for daily backups, 12 months for monthly backups
- **Location**: Encrypted S3 bucket with cross-region replication

#### Backup Procedure
```bash
# Manual backup command
kubectl exec -it postgres-instance -- pg_dump -U postgres -d todo_db > backup-$(date +%Y%m%d-%H%M%S).sql

# Scheduled backup using cron job
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: database
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres-service -U $POSTGRES_USER -d $POSTGRES_DB | \
              gzip | \
              aws s3 cp - s3://todo-platform-backups/postgres/backup-$(date +%Y%m%d-%H%M%S).sql.gz \
              --sse AES256
            env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: username
            - name: POSTGRES_DB
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: database
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
          restartPolicy: OnFailure
```

#### Backup Verification
- Automated verification of backup integrity
- Test restores performed weekly on staging environment
- Backup checksums stored separately for validation

### 2. Kafka Topic Backups

Kafka data is inherently replicated, but for long-term archival:

```bash
# MirrorMaker2 for cross-cluster replication
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaMirrorMaker2
metadata:
  name: todo-mm2
  namespace: kafka
spec:
  version: 3.6.0
  replicas: 1
  connectCluster: "target-cluster"
  clusters:
  - alias: "source"
    bootstrapServers: my-source-cluster-kafka-bootstrap:9092
  - alias: "target"
    bootstrapServers: my-target-cluster-kafka-bootstrap:9092
  mirrors:
  - sourceCluster: "source"
    targetCluster: "target"
    sourceConnector:
      config:
        replication.factor: 1
        offset-syncs.topic.replication.factor: 1
        replication.policy.separator: "."
    checkpointConnector:
      config:
        replication.factor: 1
    heartbeatConnector:
      config:
        replication.factor: 1
    topicsPattern: "todo-.*"
    groupsPattern: "todo-.*"
```

### 3. Application Configuration Backups

- Helm chart values stored in Git with proper access controls
- Dapr component configurations backed up to encrypted storage
- Kubernetes manifests version-controlled in Git

## Disaster Recovery Procedures

### 1. Service Outage Recovery

#### Immediate Actions (0-30 minutes)
1. **Assess the situation**
   - Check monitoring dashboards
   - Identify affected services
   - Determine scope of impact

2. **Communicate**
   - Notify incident response team
   - Update status page if customer-facing services affected

3. **Mitigate**
   - Scale up healthy instances if possible
   - Redirect traffic if alternative deployment exists
   - Implement circuit breakers to prevent cascading failures

#### Short-term Recovery (30 minutes - 4 hours)
1. **Restore services**
   - Deploy from last known good configuration
   - Verify service functionality
   - Monitor for stability

2. **Validate data integrity**
   - Run data consistency checks
   - Verify business logic operations

#### Long-term Recovery (4+ hours)
1. **Full restoration**
   - Restore from latest backup if needed
   - Rebuild affected components
   - Perform comprehensive testing

### 2. Data Loss Recovery

#### Database Restoration
```bash
# Restore from backup
kubectl exec -it postgres-instance -- psql -U postgres -d todo_db < backup-file.sql

# Or use a job for restoration
apiVersion: batch/v1
kind: Job
metadata:
  name: postgres-restore
  namespace: database
spec:
  template:
    spec:
      containers:
      - name: postgres-restore
        image: postgres:15
        command:
        - /bin/sh
        - -c
        - |
          aws s3 cp s3://todo-platform-backups/postgres/latest-backup.sql.gz - | \
          gunzip | \
          psql -h postgres-service -U $POSTGRES_USER -d $POSTGRES_DB
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: database
        - name: PGPASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
      restartPolicy: Never
```

#### Kafka Topic Restoration
For Kafka, we rely on:
- Replication factor ≥ 3 for critical topics
- Multiple availability zones
- Cross-cluster mirroring for disaster recovery

### 3. Regional Failover

#### DNS-Based Failover
```yaml
# Example DNS failover configuration
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: todo-platform-failover
spec:
  hosts:
  - api.todo-platform.com
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: main-api-primary
        subset: canary
      weight: 100
  - route:
    - destination:
        host: main-api-primary
        subset: stable
      weight: 90
    - destination:
        host: main-api-secondary
        subset: stable
      weight: 10
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: main-api-primary
spec:
  host: main-api-primary
  subsets:
  - name: stable
    labels:
      version: stable
  - name: canary
    labels:
      version: canary
```

## Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)

| Service | RTO | RPO | Notes |
|---------|-----|-----|-------|
| Main API | 15 minutes | 5 minutes | Auto-scaling helps rapid recovery |
| Database | 1 hour | 15 minutes | Daily backups, WAL shipping |
| Event Processing | 30 minutes | 5 minutes | Kafka replication handles most failures |
| User Authentication | 15 minutes | 5 minutes | Critical for all operations |

## Testing Procedures

### 1. Backup Verification Tests
- Weekly: Verify backup file integrity
- Monthly: Perform test restore to staging environment
- Quarterly: Full disaster recovery simulation

### 2. DR Simulation
```bash
# Chaos engineering experiment
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: database-outage
spec:
  selector:
    labelSelectors:
      app: postgres
  mode: all
  action: pod-kill
  gracePeriod: 0
  duration: 5m
  scheduler:
    cron: "@every 1h"
```

## Business Continuity Planning

### 1. Incident Response Team
- **Incident Commander**: Overall coordination
- **Technical Lead**: Technical decisions and recovery
- **Communications Lead**: Stakeholder updates
- **Customer Support Lead**: User communications

### 2. Escalation Matrix
- Level 1: Automated alerts to on-call engineer
- Level 2: Page team lead if not acknowledged in 15 minutes
- Level 3: Page manager if not resolved in 1 hour
- Level 4: Executive notification for >4 hour outages

### 3. Communication Templates
- Customer notification template
- Internal team notification template
- Executive briefing template

## Security Considerations

### 1. Backup Encryption
- All backups encrypted at rest
- Keys managed through cloud KMS or HashiCorp Vault
- Access logs maintained for all backup operations

### 2. Access Controls
- Principle of least privilege for backup access
- Regular rotation of backup credentials
- Audit trail for all restore operations

## Maintenance

### 1. Regular Reviews
- Monthly: Review backup logs and success rates
- Quarterly: Update procedures based on learnings
- Annually: Full review of DR plan effectiveness

### 2. Staff Training
- Quarterly: DR procedure training for team members
- Bi-annually: Full disaster simulation exercise
- Annually: Update contact information and escalation procedures

## Appendices

### A. Contact Information
- On-call engineer: [contact method]
- Emergency contacts: [contact methods]
- Vendor contacts: [contact information]

### B. Critical System Information
- Backup locations: [detailed locations]
- Recovery procedures: [step-by-step guides]
- System dependencies: [dependency maps]