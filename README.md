# Petadel PolicyAssist AI

## Overview

Petadel PolicyAssist AI is a prototype AI-powered policy assistant developed for Petadel Technology Services (PTS).

The application helps users locate and understand approved internal policies through natural-language questions.

The project demonstrates how AI Project Management principles can be applied to a working AI product.

## Purpose

PolicyAssist addresses the difficulty employees may experience when searching for and interpreting internal policy information.

The system is designed to:

* Retrieve relevant policy information.
* Use authoritative and active policy sources.
* Generate grounded responses.
* Provide supporting policy citations.
* Refuse unsupported questions rather than inventing information.
* Support policy governance and access considerations.

## Core AI Architecture

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
Llama 3.2 3B
       ↓
Grounded Response
       ↓
Citation
       ↓
Streamlit Interface
```

## Technology Stack

| Technology            | Role                                     |
| --------------------- | ---------------------------------------- |
| Python                | Programming language                     |
| Streamlit             | Application and user interface framework |
| Sentence Transformers | Embedding framework                      |
| all-MiniLM-L6-v2      | Embedding model                          |
| ChromaDB              | Vector database                          |
| Ollama                | Local AI runtime                         |
| Llama 3.2 3B          | Large language model                     |

## Policy Governance

PolicyAssist follows the rule:

> **Active + Authoritative + Approved + Required Metadata Present = Eligible For Retrieval**

Draft, superseded, unverified, or unresolved conflicting policies should not automatically be treated as authoritative sources.

## Quality Targets

The project establishes the following targets:

* Retrieval Accuracy ≥ 90%
* Answer Accuracy ≥ 90%
* Hallucination Rate < 2%
* Citation Correctness = 100%
* Unsupported-Question Refusal = 100%
* Response Latency ≤ 10 seconds
* User Satisfaction ≥ 85%

These targets require formal evaluation evidence before production readiness can be claimed.

## Current Status

**MVP Prototype Demonstration Complete**

The prototype demonstrates the core AI policy-assistance workflow.

Formal:

* AI evaluation
* Security validation
* Testing
* UAT
* Pilot
* Monitoring validation
* Rollback validation
* Governance approval
* Production release

remain separate production-readiness activities.

## Project Relationship

PolicyAssist is the working AI application used as the technical laboratory for the AI Project Management Course.

The course demonstrates the Project Management discipline surrounding the application, including:

* Business analysis
* Requirements
* Agile planning
* AI architecture
* Data governance
* AI evaluation
* Risk management
* Security
* UAT
* Release management
* Monitoring
* Evidence-based decision-making

## Running The Application

The application is designed to run locally using Python, Streamlit, and Ollama.

See the project setup instructions before running the application.

## Project Principle

> **A functioning AI prototype is not automatically a production-ready AI product.**

Production readiness requires evidence across business, technical, data, security, governance, quality, user acceptance, and operational requirements.
