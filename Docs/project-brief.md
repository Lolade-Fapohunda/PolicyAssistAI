# PolicyAssist — AI PM Capstone

## 1. Project Overview

PolicyAssist is an AI-powered policy assistant designed to help authorized employees quickly find and understand organizational policies.

The system uses retrieval and generative AI to provide grounded answers, identify authoritative policy sources, and escalate questions when the system cannot safely provide a reliable answer.

## 2. Business Problem

Employees may spend significant time searching through large collections of policy documents to locate the correct information.

The problem is made more difficult when:

- Policies exist in PDF or scanned formats.
- Multiple versions of a policy may exist.
- Different departments may maintain different versions.
- Employees may not know the exact title or terminology used in a policy.
- Users may have different access permissions.
- AI-generated answers must be supported by authoritative sources.

## 3. Product Goal

Provide an easy-to-use AI interface that allows authorized users to ask policy questions in natural language and receive reliable, source-supported answers.

## 4. MVP Scope

The Minimum Viable Product (MVP) will support:

- Natural-language policy questions
- Policy document retrieval
- Semantic search using embeddings
- Retrieval-Augmented Generation (RAG)
- Source citations
- Policy version awareness
- Authorization controls
- Human escalation
- User feedback
- Basic monitoring
- Response caching where appropriate

## 5. Success Measures

Initial MVP targets:

| Measure | Target |
|---|---:|
| Policy answer accuracy | ≥90% |
| Hallucination rate | <2% |
| Response latency | ≤10 seconds |
| Source/citation accuracy | Defined during evaluation |
| Unauthorized information disclosure | 0 accepted incidents |

## 6. Primary Users

### Employees

Employees who need to locate and understand organizational policies.

### Policy Owners

Individuals responsible for maintaining and approving organizational policies.

### Administrators

Individuals responsible for managing access, system configuration, and monitoring.

## 7. Key Product Principles

1. Security and authorization are enforced independently of the AI model.
2. The system should prefer authoritative information over convenience.
3. The system should not fabricate answers when sufficient evidence is unavailable.
4. Human escalation should be available when human judgment is required.
5. AI performance must be measured rather than assumed.
6. The MVP should remain intentionally small and focused.

## 8. Out of Scope for MVP

The initial MVP will not include:

- Voice interaction
- Autonomous decision-making
- Complex agentic workflows
- Enterprise Single Sign-On (SSO)
- Advanced analytics dashboards
- Multi-modal interfaces
- Automated policy approval
- Automated policy changes

These capabilities may be considered in a future product roadmap.

## 9. Project Approach

PolicyAssist will be developed incrementally using an Agile delivery approach.

The project will move through:

**Initiation → Discovery → Requirements → Planning → AI Design → Development → Testing → Release → Production → Continuous Improvement**

## 10. Capstone Objective

The project demonstrates the ability to manage an AI product from problem definition through delivery and operational improvement.

The emphasis is on AI Project Management rather than software engineering alone.