# Petadel PolicyAssist AI

An AI-powered policy assistant prototype built as the technical capstone for the Petadel AI Project Management Course.

PolicyAssist helps employees retrieve relevant policy information and receive responses grounded in approved policy evidence.

## Project Overview

**Organization:** Petadel Technology Services (PTS)
**Product:** Petadel PolicyAssist AI
**Project Role:** AI Project Manager / Product Owner perspective
**Architecture:** Retrieval-Augmented Generation (RAG)
**Application:** Streamlit
**Status:** Prototype / MVP Evaluation
**Current Production Decision:** HOLD

## Business Problem

Employees may spend significant time searching for policies, determining which version is current, and understanding how policies apply to their situation.

PolicyAssist was designed to provide a centralized, searchable interface for retrieving relevant policy evidence.

## Core Workflow

```text
Policy Documents
      ↓
Document Processing
      ↓
Chunking
      ↓
Embeddings
      ↓
ChromaDB
      ↓
Semantic Retrieval
      ↓
Policy Eligibility Validation
      ↓
Response Generation
      ↓
Grounding + Citation
      ↓
Employee Response
```

The system is designed to answer from retrieved policy evidence rather than relying solely on general model knowledge.

## Technology Stack

| Technology            | Purpose                                  |
| --------------------- | ---------------------------------------- |
| Python                | Application development                  |
| Streamlit             | User interface                           |
| Sentence Transformers | Text embeddings                          |
| `all-MiniLM-L6-v2`    | Embedding model                          |
| ChromaDB              | Vector database                          |
| Google Gen AI         | Cloud model integration                  |
| Gemini 2.5 Flash      | Deployed response-generation model       |
| Ollama                | Local model runtime                      |
| Llama 3.2 3B          | Local fallback response-generation model |

## Model Configuration

### Deployed

The deployed Streamlit application uses:

**Google Gen AI → Gemini 2.5 Flash**

When the required Gemini API key is available, Gemini 2.5 Flash generates responses using the retrieved policy evidence.

### Local Development / Fallback

The application also supports:

**Ollama → Llama 3.2 3B**

This provides a local response-generation option when the Gemini API key is unavailable.

The retrieval and grounding workflow remains the same across the configurations.

## Key Design Principles

### Grounded Responses

Responses should be supported by retrieved policy evidence.

### Citation

The application provides supporting policy information so users can verify the source of an answer.

### Do Not Invent

When sufficient evidence is unavailable, the system should not create a policy requirement that is not supported by the available evidence.

### Authority

Policy documents should be evaluated based on characteristics such as:

* Active status
* Authority
* Approval
* Version
* Effective date
* Required metadata

### Escalation

Questions that cannot be answered reliably from available evidence should be identified for human review or escalation.

## Project Quality Targets

The project established the following target measures:

| Measure            |       Target |
| ------------------ | -----------: |
| Retrieval accuracy |        ≥ 90% |
| Hallucination rate |         < 2% |
| Response latency   | ≤ 10 seconds |

These are project targets requiring formal validation. The existence of a working prototype does not mean the targets have been fully demonstrated.

## Testing and Evaluation

Evaluation scenarios include:

* Standard policy questions
* Unsupported questions
* Multi-policy questions
* Conflicting policy information
* Citation verification
* Retrieval accuracy
* Response accuracy
* Hallucination behavior
* Response latency
* Security and access-control scenarios

## Security Considerations

A production implementation must include appropriate:

* Authentication
* Authorization
* Role-based access
* Document access controls
* Sensitive information protection
* Audit logging
* Unauthorized-access testing

Retrieval relevance does not automatically mean that a user is authorized to access the retrieved information.

## MVP vs. Production

The prototype demonstrates the core technical workflow:

* Policy document ingestion
* Embedding generation
* Vector retrieval
* Policy eligibility
* Response generation
* Grounding
* Citation
* User interaction

However, a functioning prototype is not equivalent to production readiness.

Production deployment requires additional evidence for:

* AI quality
* Security
* Governance
* Performance
* User acceptance testing
* Monitoring
* Risk controls
* Rollback
* Operational readiness

## Current Project Decision

**HOLD**

The prototype demonstrates technical feasibility, but production release is not approved.

The HOLD decision remains in place until the required evaluation, security, governance, testing, monitoring, and release-readiness evidence has been completed and reviewed.

## Project Management Perspective

This repository is part of an AI Project Management capstone demonstrating that an AI Project Manager must manage more than the technology itself.

Key project-management responsibilities include:

* Requirements
* Stakeholder management
* Product planning
* AI architecture decisions
* Data governance
* Risk management
* Security
* AI evaluation
* Testing and UAT
* Release readiness
* Monitoring
* Change management
* Go / Hold / No-Go decisions

## Related Course Repository

The PolicyAssist project is the capstone for the **AI Project Management Course** and demonstrates the complete project lifecycle from initiation through evaluation and release readiness.

The project emphasizes a central principle:

> A working AI prototype demonstrates technical feasibility. It does not, by itself, demonstrate production readiness.
