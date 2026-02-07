# Comprehensive Hackathon Test Plan (Phases I-V)

## Overview
This test plan validates the complete 5-phase Hackathon-Todo project. All phases have been implemented and are ready for comprehensive end-to-end testing.

## Test Environment Setup

### Prerequisites
- Python 3.13+
- UV package manager
- Docker and Docker Compose
- Minikube or access to Kubernetes cluster
- Dapr CLI
- kubectl
- Node.js 18+ (for frontend)

### Environment Configuration
1. Clone the repository
2. Navigate to project root
3. Set up Python virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```
4. Install backend dependencies:
   ```bash
   cd backend
   uv pip install -r requirements.txt
   ```
5. Install frontend dependencies:
   ```bash
   cd ../frontend
   npm install
   ```

## Phase I Tests - Basic Console Application

### Test 1.1: Basic Todo Operations
1. Start the console application
2. Verify ability to add tasks with titles
3. Verify ability to list tasks
4. Verify ability to mark tasks as complete
5. Verify ability to delete tasks
6. Verify tasks persist in memory during session

### Test 1.2: Command Parsing
1. Test various command formats
2. Verify error handling for invalid commands
3. Verify proper response messages

## Phase II Tests - Multi-User Web Application

### Test 2.1: User Authentication
1. Navigate to registration page
2. Register a new user account
3. Verify account creation with proper validation
4. Login with the new account
5. Verify JWT token handling
6. Test logout functionality

### Test 2.2: Multi-User Isolation
1. Register two different user accounts
2. Create tasks for user 1
3. Login as user 2 and verify they cannot see user 1's tasks
4. Create tasks for user 2
5. Login back as user 1 and verify they cannot see user 2's tasks

### Test 2.3: Web UI Functionality
1. Test task creation through web interface
2. Test task listing and display
3. Test task editing and updating
4. Test task completion toggling
5. Test task deletion

## Phase III Tests - AI-Powered Conversational Chatbot

### Test 3.1: Natural Language Processing
1. Access the chatbot interface
2. Test adding tasks with natural language: "Add task: buy groceries tomorrow"
3. Test querying tasks: "Show my tasks"
4. Test updating tasks: "Mark task 1 as complete"
5. Verify proper parsing of natural language commands

### Test 3.2: MCP Integration
1. Verify AI agent properly calls backend tools via MCP
2. Test tool chaining for multi-action commands
3. Verify conversation history persistence
4. Test error handling when MCP tools fail

### Test 3.3: Multi-User Chatbot Isolation
1. Test chatbot functionality with different user sessions
2. Verify user isolation in conversation history
3. Confirm tasks created by one user are not visible to another

## Phase IV Tests - Local Kubernetes Deployment

### Test 4.1: Kubernetes Cluster Setup
1. Start Minikube cluster
2. Verify cluster is running: `minikube status`
3. Install Dapr: `dapr init -k`
4. Verify Dapr is running: `kubectl get pods -n dapr-system`

### Test 4.2: Helm Chart Deployment
1. Deploy application using Helm:
   ```bash
   helm install todo-platform infrastructure/helm-charts/todo-platform/
   ```
2. Verify all pods are running: `kubectl get pods`
3. Verify services are accessible: `kubectl get services`
4. Verify Dapr applications: `kubectl get daprapps`

### Test 4.3: Service Connectivity
1. Verify frontend service is accessible
2. Verify backend API service connectivity
3. Test basic functionality through Kubernetes services
4. Verify inter-service communication

## Phase V Tests - Cloud-Native Event-Driven Architecture

### Test 5.1: Microservices Architecture
1. Verify main API service functionality
2. Verify recurring task service operation
3. Verify notification service operation
4. Verify audit service operation
5. Test service-to-service communication via Dapr

### Test 5.2: Event-Driven Architecture
1. Create a task and verify "task-created" event is published
2. Update a task and verify "task-updated" event is published
3. Complete a task and verify "task-completed" event is published
4. Verify events are consumed by appropriate services
5. Test event ordering and correlation

### Test 5.3: Kafka Integration
1. Verify Kafka topics exist: task-events, reminders, task-updates
2. Test event publishing to Kafka via Dapr pub/sub
3. Verify event consumption by services
4. Test event durability and at-least-once delivery

### Test 5.4: Advanced Task Features
1. Test priority assignment (low, medium, high)
2. Test tag assignment and filtering
3. Test due date functionality
4. Test reminder scheduling via Dapr Jobs API
5. Test recurring task creation (daily, weekly, monthly)

### Test 5.5: AI Subagent Integration
1. Test Task Interpretation Agent with natural language input
2. Test Scheduling Intelligence Agent for due date suggestions
3. Test Reminder Reasoning Agent for optimal timing
4. Verify fallback mechanisms when AI subagents unavailable

### Test 5.6: Multi-Tenant Security
1. Create tasks for different users
2. Verify user data isolation
3. Test row-level security in PostgreSQL
4. Verify user context propagation through Dapr metadata
5. Test mTLS communication between services

### Test 5.7: Production Readiness
1. Test horizontal pod autoscaling
2. Verify health check endpoints
3. Test pod restart resilience
4. Verify backup and recovery procedures
5. Test load handling under stress

## Integration Tests - Cross-Phase Functionality

### Test 6.1: End-to-End User Journey
1. Register new user via web interface
2. Create tasks using AI chatbot
3. Verify tasks appear in web UI
4. Update tasks via web UI
5. Verify updates reflected in chatbot
6. Complete tasks and verify through all interfaces

### Test 6.2: Event Flow Validation
1. Create task via web UI
2. Verify event published to Kafka
3. Verify recurring task service processes event
4. Verify audit service logs event
5. Verify notification service processes relevant events

### Test 6.3: Performance Validation
1. Measure API response times (<300ms p95)
2. Verify reminder execution timing (≤60 seconds tolerance)
3. Test concurrent user handling
4. Validate system stability under load

## Test Execution Instructions

### For Beginner Orchestrator:
1. Follow the tests in numerical order (Test 1.1, 1.2, 2.1, etc.)
2. Each test should pass before proceeding to the next
3. Document any failures with specific error messages
4. Restart services if needed between major test sections
5. Use the acceptance criteria from each phase's specification to validate results

### Expected Results:
- All Phase I-V functionality should work as specified
- No Phase VI features should be active or accessible
- System should be fully operational in Kubernetes environment
- All user isolation and security measures should be functional
- Event-driven architecture should operate correctly
- AI subagents should enhance functionality as designed

## Success Criteria
- ✅ All individual tests pass
- ✅ Cross-phase integration works seamlessly
- ✅ Multi-tenant isolation maintained
- ✅ Performance requirements met
- ✅ Security measures functional
- ✅ Event-driven architecture operational
- ✅ AI enhancements working properly
- ✅ System deployable and operational in Kubernetes