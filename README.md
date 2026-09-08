# Petadel PolicyAssist AI

## Overview

Petadel PolicyAssist AI is a working prototype policy assistant developed for Petadel Technology Services (PTS).

The application helps users locate and understand approved internal policies through natural-language questions.

The project demonstrates how project management principles can be applied to a working AI product.

## Purpose

PolicyAssist addresses the difficulty employees may experience when searching for and interpreting internal policy information.

The system is designed to:

* Retrieve relevant policy information.
* Use authoritative and active policy sources.
* Generate responses supported by policy evidence.
* Provide supporting policy citations.
* Refuse unsupported questions rather than invent information.
* Support policy governance and access considerations.

## Core Architecture

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
Response Generation
       ↓
Grounded Response
       ↓
Citation
       ↓
Streamlit Interface
```

## Response Generation

The application supports two response-generation configurations.

### Deployed Configuration

When `GEMINI_API_KEY` is configured, the application uses:

**Google Gen AI → Gemini 2.5 Flash**

### Local Development Configuration

When the Gemini API key is not available, the application can use:

**Ollama → Llama 3.2 3B**

The application code contains both configurations and selects the Gemini path when the API key is available.

## Technology Stack

| Technology            | Role                                           |
| --------------------- | ---------------------------------------------- |
| Python                | Programming language                           |
| Streamlit             | Application and user interface                 |
| Sentence Transformers | Embedding framework                            |
| `all-MiniLM-L6-v2`    | Embedding model                                |
| ChromaDB              | Vector database                                |
| Google Gen AI         | Cloud model integration                        |
| Gemini 2.5 Flash      | Response generation for deployed configuration |
| Ollama                | Local model runtime                            |
| Llama 3.2 3B          | Local response-generation fallback             |

## Policy Governance

PolicyAssist follows the rule:

> **Active + Authoritative + Approved + Required Metadata Present = Eligible For Retrieval**

Draft, superseded, unverified, or unresolved conflicting policies should not automatically be treated as authoritative sources.

## Response Principle

When sufficient policy evidence exists:

**Retrieve → Ground → Answer → Cite**

When sufficient authoritative evidence does not exist:

**Do Not Invent → Refuse or Escalate**

The response-generation model is not treated as an independent source of company policy.

## Quality Targets

The project establishes the following targets:

* Retrieval Accuracy ≥ 90%
* Answer Accuracy ≥ 90%
* Hallucination Rate < 2%
* Citation Correctness = 100%
* Unsupported-Question Refusal = 100%
* Response Latency ≤ 10 seconds
* User Satisfaction ≥ 85%
* Critical Security Incidents = 0

These targets require formal evaluation evidence before production readiness can be claimed.

## Project Status

The application is a working prototype.

The current project decision is:

**HOLD**

The prototype demonstrates the core policy-assistance workflow, but production release requires additional evidence covering evaluation, UAT, security validation, monitoring, rollback, governance, and final release approval.

## Project Management Context

Petadel PolicyAssist AI is the capstone project for the AI Project Management Course.

The project demonstrates:

* Business problem definition
* Requirements management
* Product planning
* Architecture decision-making
* Data governance
* Evaluation
* Risk management
* Security
* Testing
* UAT
* Release readiness
* Monitoring
* Continuous improvement
* Evidence-based decision-making
