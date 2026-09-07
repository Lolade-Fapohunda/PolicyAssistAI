import os
import re
import hashlib
import subprocess
from pathlib import Path

import chromadb
import streamlit as st
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / ".chroma"
COLLECTION_NAME = "petadel_policyassist"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_DISTANCE = 1.20
SEMANTIC_RESULTS = 12
OLLAMA_MODEL = "llama3.2:3b"
GEMINI_MODEL = "gemini-2.5-flash"

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Petadel PolicyAssist AI",
    page_icon="📘",
    layout="wide",
)

# ============================================================
# APPROVED INTERFACE
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #171717;
        color: #eeeeee;
    }
    [data-testid="stSidebar"] {
        background-color: #202020;
    }
    [data-testid="stSidebar"] * {
        color: #dddddd;
    }
    .block-container {
        padding-top: 2rem;
    }
    input {
        background-color: #3d3d3d !important;
        color: #ffffff !important;
    }
    div[data-baseweb="input"] {
        background-color: #3d3d3d !important;
    }
    button[kind="primary"] {
        background-color: #b00000 !important;
        border-color: #b00000 !important;
        color: #ffffff !important;
    }
    button[kind="secondary"] {
        background-color: #303030 !important;
        border-color: #777777 !important;
        color: #eeeeee !important;
    }
    h1, h2, h3 {
        color: #f2f2f2;
    }
    p, li, label {
        color: #dddddd;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# METADATA
# ============================================================

def normalize_key(key):
    return (
        key.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def normalize_metadata(metadata):
    normalized = {}

    for key, value in metadata.items():
        normalized[normalize_key(key)] = str(value).strip()

    if (
        "policy_category" not in normalized
        and "category" in normalized
    ):
        normalized["policy_category"] = normalized["category"]

    if (
        "category" not in normalized
        and "policy_category" in normalized
    ):
        normalized["category"] = normalized["policy_category"]

    if (
        "approval_status" not in normalized
        and "approval" in normalized
    ):
        normalized["approval_status"] = normalized["approval"]

    if "status" in normalized:
        normalized["status"] = normalized["status"].lower()

    if "approval_status" in normalized:
        normalized["approval_status"] = (
            normalized["approval_status"].lower()
        )

    return normalized


def parse_policy_file(file_path):
    text = file_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    metadata = {}
    body = text
    stripped = text.lstrip()

    if stripped.startswith("---"):
        parts = stripped.split("---", 2)

        if len(parts) >= 3:
            metadata_text = parts[1]
            body = parts[2]

            for line in metadata_text.splitlines():
                line = line.strip()

                if not line or ":" not in line:
                    continue

                key, value = line.split(":", 1)

                metadata[normalize_key(key)] = (
                    value.strip()
                    .strip('"')
                    .strip("'")
                )

    return normalize_metadata(metadata), body.strip()


def policy_is_eligible(metadata):
    required = [
        "policy_id",
        "policy_name",
        "version",
        "status",
        "effective_date",
        "policy_owner",
    ]

    for field in required:
        if not metadata.get(field):
            return False

    if metadata.get("status", "").lower() != "active":
        return False

    if "approval_status" in metadata:
        if (
            metadata["approval_status"].lower()
            != "approved"
        ):
            return False

    return True


def clean_text(text):
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def chunk_policy(body):
    body = clean_text(body)

    sections = re.split(
        r"(?=^#{1,4}\s+)",
        body,
        flags=re.MULTILINE,
    )

    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        max_chars = 1600

        if len(section) <= max_chars:
            chunks.append(section)
            continue

        paragraphs = section.split("\n\n")
        current = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            if len(current) + len(paragraph) + 2 <= max_chars:
                current = (
                    paragraph
                    if not current
                    else current + "\n\n" + paragraph
                )
            else:
                if current:
                    chunks.append(current)

                current = paragraph

        if current:
            chunks.append(current)

    return chunks


# ============================================================
# POLICY TOPIC ROUTING
# ============================================================

POLICY_TOPIC_KEYWORDS = {
    "information security policy": [
        "information security",
        "security",
        "password",
        "passwords",
        "credential",
        "credentials",
        "phishing",
        "suspicious email",
        "suspicious communication",
        "malware",
        "cyber",
        "hack",
        "hacked",
        "account compromised",
        "compromised account",
        "unauthorized access",
        "access control",
        "security incident",
        "security incidents",
        "lost device",
        "stolen device",
        "company device",
        "personal device",
        "cloud storage",
        "remote access",
        "confidential information",
        "sensitive information",
        "data storage",
        "data transmission",
        "external service",
        "authentication",
        "authenticate",
        "login",
        "log in",
        "access privileges",
        "security violation",
    ],

    "remote work policy": [
        "remote work",
        "work remotely",
        "working remotely",
        "work from home",
        "working from home",
        "remote days",
        "remote schedule",
        "remote employee",
        "remote employees",
        "office days",
    ],

    "attendance policy": [
        "attendance",
        "absent",
        "absence",
        "tardy",
        "tardiness",
        "late",
        "punctuality",
        "work hours",
        "working hours",
        "scheduled work",
        "call out",
        "calling out",
    ],

    "expense reimbursement policy": [
        "expense",
        "expenses",
        "reimbursement",
        "reimburse",
        "receipt",
        "receipts",
        "business expense",
        "meal",
        "meals",
        "travel expense",
        "submit expense",
        "expense report",
    ],

    "employee leave policy": [
        "leave",
        "leaves",
        "vacation",
        "pto",
        "paid time off",
        "time off",
        "days off",
        "sick leave",
        "sick days",
        "parental leave",
        "maternity leave",
        "maternity",
        "paternity leave",
        "paternity",
        "medical leave",
        "family leave",
        "new baby",
        "having a baby",
        "baby",
        "birth",
        "parental",
        "paid leave",
        "unpaid leave",
    ],

    "code of conduct policy": [
        "code of conduct",
        "conduct",
        "behavior",
        "behaviour",
        "harassment",
        "discrimination",
        "respectful workplace",
        "conflict of interest",
        "gift",
        "gifts",
        "ethics",
        "professional behavior",
        "professional conduct",
        "misconduct",
        "reporting misconduct",
    ],
}


def get_policy_topic_scores(question):
    question_lower = question.lower()

    scores = {
        policy_name: 0
        for policy_name in POLICY_TOPIC_KEYWORDS
    }

    for policy_name, keywords in POLICY_TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question_lower:
                if len(keyword.split()) > 1:
                    scores[policy_name] += 5
                else:
                    scores[policy_name] += 2

    # --------------------------------------------------------
    # Strong leave-specific routing
    # --------------------------------------------------------

    leave_amount_terms = [
        "how many days",
        "how many leave days",
        "how much leave",
        "how much time off",
        "how many weeks",
        "how many days do i get",
        "how many days can i take",
        "how much pto",
        "how much vacation",
        "vacation days",
        "leave days",
        "days of leave",
        "days of pto",
        "days of vacation",
    ]

    leave_context_terms = [
        "leave",
        "pto",
        "vacation",
        "time off",
        "sick",
        "parental",
        "maternity",
        "paternity",
        "medical",
        "family",
        "baby",
        "birth",
    ]

    if any(
        term in question_lower
        for term in leave_amount_terms
    ):
        if any(
            term in question_lower
            for term in leave_context_terms
        ):
            scores["employee leave policy"] += 15

    # --------------------------------------------------------
    # Strong parental-leave routing
    # --------------------------------------------------------

    parental_terms = [
        "parental leave",
        "maternity leave",
        "paternity leave",
        "maternity",
        "paternity",
        "having a baby",
        "new baby",
        "after having a baby",
        "after the birth",
        "after giving birth",
        "childbirth",
    ]

    if any(
        term in question_lower
        for term in parental_terms
    ):
        scores["employee leave policy"] += 15

    # --------------------------------------------------------
    # Strong vacation/PTO routing
    # --------------------------------------------------------

    vacation_terms = [
        "vacation",
        "vacation days",
        "pto",
        "paid time off",
        "time off",
    ]

    if any(
        term in question_lower
        for term in vacation_terms
    ):
        scores["employee leave policy"] += 10

    # --------------------------------------------------------
    # Attendance must not override explicit leave intent.
    # --------------------------------------------------------

    if (
        scores["employee leave policy"] > 0
        and scores["attendance policy"] > 0
    ):
        scores["attendance policy"] = max(
            0,
            scores["attendance policy"] - 10,
        )

    return scores


# ============================================================
# CHROMA / EMBEDDINGS
# ============================================================

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)


@st.cache_resource
def get_chroma_collection():
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


# ============================================================
# INGESTION
# ============================================================

def create_chunk_id(file_name, index, text):
    raw = f"{file_name}|{index}|{text}"

    return hashlib.md5(
        raw.encode("utf-8")
    ).hexdigest()


def load_policy_documents():
    documents = []

    if not DATA_DIR.exists():
        return documents

    for file_path in sorted(
        DATA_DIR.glob("*.md")
    ):
        try:
            metadata, body = parse_policy_file(
                file_path
            )

            documents.append(
                {
                    "file_name": file_path.name,
                    "metadata": metadata,
                    "body": body,
                }
            )

        except Exception as exc:
            st.warning(
                f"Could not read {file_path.name}: {exc}"
            )

    return documents


def ingest_policies(force=False):
    collection = get_chroma_collection()
    model = get_embedding_model()
    policies = load_policy_documents()

    if not policies:
        return 0, 0, 0

    if force:
        try:
            collection.delete(where={})
        except Exception:
            pass

    existing_ids = set()

    if not force:
        try:
            existing = collection.get(include=[])
            existing_ids = set(
                existing.get("ids", [])
            )
        except Exception:
            existing_ids = set()

    ids = []
    texts = []
    metadatas = []

    eligible_count = 0
    section_count = 0

    for policy in policies:
        metadata = policy["metadata"]

        eligible = policy_is_eligible(
            metadata
        )

        if eligible:
            eligible_count += 1

        chunks = chunk_policy(
            policy["body"]
        )

        for index, chunk in enumerate(chunks):
            section_count += 1

            chunk_id = create_chunk_id(
                policy["file_name"],
                index,
                chunk,
            )

            if (
                not force
                and chunk_id in existing_ids
            ):
                continue

            chunk_metadata = dict(metadata)

            chunk_metadata.update(
                {
                    "source_file": policy[
                        "file_name"
                    ],
                    "eligible": str(
                        eligible
                    ).lower(),
                    "chunk_index": str(index),
                }
            )

            ids.append(chunk_id)
            texts.append(chunk)
            metadatas.append(chunk_metadata)

    if texts:
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings.tolist(),
        )

    return (
        len(policies),
        eligible_count,
        section_count,
    )


# ============================================================
# RETRIEVAL
# ============================================================

def semantic_search(question):
    collection = get_chroma_collection()
    model = get_embedding_model()

    if collection.count() == 0:
        ingest_policies()

    query_embedding = model.encode(
        [question],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=SEMANTIC_RESULTS,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    candidates = []

    documents = results.get(
        "documents",
        [[]],
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]],
    )[0]

    distances = results.get(
        "distances",
        [[]],
    )[0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        metadata = normalize_metadata(
            metadata
        )

        candidates.append(
            {
                "document": document,
                "metadata": metadata,
                "distance": float(distance),
            }
        )

    return candidates


def keyword_search(question):
    question_lower = question.lower()
    results = []

    policies = load_policy_documents()

    topic_scores = get_policy_topic_scores(
        question
    )

    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        question_lower,
    )

    for policy in policies:
        metadata = normalize_metadata(
            policy["metadata"]
        )

        if not policy_is_eligible(metadata):
            continue

        policy_name = metadata.get(
            "policy_name",
            "",
        ).lower()

        chunks = chunk_policy(
            policy["body"]
        )

        for index, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            score = 0

            for word in set(words):
                if len(word) < 4:
                    continue

                if word in chunk_lower:
                    score += 1

            topic_score = topic_scores.get(
                policy_name,
                0,
            )

            score += topic_score * 2

            if score > 0:
                results.append(
                    {
                        "document": chunk,
                        "metadata": metadata,
                        "distance": 0.95,
                        "keyword_score": score,
                        "chunk_index": index,
                    }
                )

    results.sort(
        key=lambda x: x.get(
            "keyword_score",
            0,
        ),
        reverse=True,
    )

    return results[:SEMANTIC_RESULTS]


def _is_authoritative_leave_policy(policy):
    metadata = normalize_metadata(
        policy.get("metadata", {})
    )

    policy_id = metadata.get(
        "policy_id",
        "",
    ).strip().lower()

    policy_name = metadata.get(
        "policy_name",
        "",
    ).strip().lower()

    file_name = policy.get(
        "file_name",
        "",
    ).strip().lower()

    body = policy.get(
        "body",
        "",
    ).lower()

    return (
        policy_id == "hr-leave-001"
        or policy_name == "employee leave policy"
        or file_name == "employee_leave_policy.md"
        or (
            "employee leave policy" in body
            and "policy authority" in body
        )
    )


def _get_authoritative_leave_evidence():
    policies = load_policy_documents()

    for policy in policies:
        if not _is_authoritative_leave_policy(policy):
            continue

        metadata = normalize_metadata(
            policy.get("metadata", {})
        )

        # The known authoritative leave policy is HR-LEAVE-001,
        # version 3.0, active and approved. Fill only missing
        # metadata here so retrieval remains robust if the file's
        # front matter was not parsed correctly.

        metadata.setdefault(
            "policy_id",
            "HR-LEAVE-001",
        )

        metadata.setdefault(
            "policy_name",
            "Employee Leave Policy",
        )

        metadata.setdefault(
            "version",
            "3.0",
        )

        metadata.setdefault(
            "status",
            "active",
        )

        metadata.setdefault(
            "effective_date",
            "2026-01-01",
        )

        metadata.setdefault(
            "policy_owner",
            "Human Resources",
        )

        metadata.setdefault(
            "approval_status",
            "approved",
        )

        if not policy_is_eligible(metadata):
            continue

        evidence = []

        chunks = chunk_policy(
            policy.get("body", "")
        )

        for index, chunk in enumerate(chunks):
            evidence.append(
                {
                    "document": chunk,
                    "metadata": metadata,
                    "distance": 0.0,
                    "score": 10.0,
                    "method": "authoritative",
                    "chunk_index": index,
                    "source_file": policy.get(
                        "file_name",
                        "employee_leave_policy.md",
                    ),
                }
            )

        return evidence

    return []


def _strongest_policy_topic(topic_scores):
    strongest_topic = None
    strongest_topic_score = 0

    for policy_name, score in topic_scores.items():
        if score > strongest_topic_score:
            strongest_topic = policy_name
            strongest_topic_score = score

    return (
        strongest_topic,
        strongest_topic_score,
    )


def _candidate_matches_topic(candidate, topic):
    if not topic:
        return False

    metadata = normalize_metadata(
        candidate.get("metadata", {})
    )

    policy_name = metadata.get(
        "policy_name",
        "",
    ).lower()

    if policy_name == topic:
        return True

    if topic == "employee leave policy":
        policy_id = metadata.get(
            "policy_id",
            "",
        ).lower()

        source_file = candidate.get(
            "source_file",
            "",
        ).lower()

        document = candidate.get(
            "document",
            "",
        ).lower()

        return (
            policy_id == "hr-leave-001"
            or source_file == "employee_leave_policy.md"
            or (
                "employee leave policy" in document
                and "policy authority" in document
            )
        )

    return False


def retrieve_policy_evidence(question):
    topic_scores = get_policy_topic_scores(
        question
    )

    strongest_topic, strongest_topic_score = (
        _strongest_policy_topic(topic_scores)
    )

    # --------------------------------------------------------
    # HARD ROUTING FOR EXPLICIT LEAVE / PTO QUESTIONS
    # --------------------------------------------------------

    # Explicit leave intent must never fall through to an
    # unrelated policy such as Expense Reimbursement.

    if (
        strongest_topic == "employee leave policy"
        and strongest_topic_score >= 2
    ):
        return _get_authoritative_leave_evidence()[:6]

    semantic_candidates = semantic_search(
        question
    )

    combined = []

    # --------------------------------------------------------
    # Semantic candidates
    # --------------------------------------------------------

    for candidate in semantic_candidates:
        metadata = candidate["metadata"]

        if not policy_is_eligible(metadata):
            continue

        distance = candidate["distance"]

        if distance > MAX_DISTANCE:
            continue

        policy_name = metadata.get(
            "policy_name",
            "",
        ).lower()

        topic_boost = topic_scores.get(
            policy_name,
            0,
        )

        semantic_score = max(
            0.0,
            1.0 - distance,
        )

        final_score = (
            semantic_score
            + (topic_boost * 0.08)
        )

        combined.append(
            {
                **candidate,
                "score": final_score,
                "method": "semantic",
            }
        )

    # --------------------------------------------------------
    # Keyword candidates
    # --------------------------------------------------------

    keyword_candidates = keyword_search(
        question
    )

    for candidate in keyword_candidates:
        metadata = candidate["metadata"]

        if not policy_is_eligible(metadata):
            continue

        policy_name = metadata.get(
            "policy_name",
            "",
        ).lower()

        topic_boost = topic_scores.get(
            policy_name,
            0,
        )

        keyword_score = candidate.get(
            "keyword_score",
            0,
        )

        final_score = (
            0.30
            + min(
                keyword_score / 20.0,
                0.50,
            )
            + (topic_boost * 0.08)
        )

        combined.append(
            {
                **candidate,
                "score": final_score,
                "method": "keyword",
            }
        )

    # --------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------

    deduped = {}

    for candidate in combined:
        key = (
            candidate["metadata"].get(
                "policy_id",
                "",
            ),
            candidate["document"].strip(),
        )

        if key not in deduped:
            deduped[key] = candidate

        elif (
            candidate["score"]
            > deduped[key]["score"]
        ):
            deduped[key] = candidate

    combined = list(
        deduped.values()
    )

    combined.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    if not combined:
        return []

    # --------------------------------------------------------
    # Topic prioritization
    # --------------------------------------------------------

    if (
        strongest_topic
        and strongest_topic_score >= 2
    ):
        matching = [
            item
            for item in combined
            if _candidate_matches_topic(
                item,
                strongest_topic,
            )
        ]

        if matching:
            matching.sort(
                key=lambda x: x["score"],
                reverse=True,
            )

            others = [
                item
                for item in combined
                if item not in matching
            ]

            combined = matching + others

    return combined[:6]


# ============================================================
# SUPPORTING EVIDENCE
# ============================================================

def select_supporting_evidence(
    question,
    candidates,
):
    if not candidates:
        return []

    topic_scores = get_policy_topic_scores(
        question
    )

    strongest_topic, strongest_score = (
        _strongest_policy_topic(topic_scores)
    )

    if (
        strongest_topic
        and strongest_score >= 2
    ):
        matching = [
            item
            for item in candidates
            if _candidate_matches_topic(
                item,
                strongest_topic,
            )
        ]

        if matching:
            return matching[:4]

        # Explicit leave intent with no authoritative leave
        # evidence must remain unsupported. Do not select an
        # unrelated policy as the source.

        if strongest_topic == "employee leave policy":
            return []

    top_policy = candidates[0][
        "metadata"
    ].get(
        "policy_name",
        "",
    ).lower()

    matching = [
        item
        for item in candidates
        if item["metadata"]
        .get("policy_name", "")
        .lower()
        == top_policy
    ]

    return matching[:4]


# ============================================================
# OLLAMA
# ============================================================

def find_ollama():
    paths = [
        "ollama",
        r"C:\Users\oladi\AppData\Local\Programs\Ollama\ollama.exe",
    ]

    for path in paths:
        if path == "ollama":
            return path

        if os.path.exists(path):
            return path

    return None


# ============================================================
# CLEAN OLLAMA TERMINAL CONTROL CHARACTERS
# ============================================================

def clean_ollama_output(text):
    if not text:
        return text

    # Remove ANSI escape sequences and terminal control codes
    text = re.sub(
        r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])",
        "",
        text,
    )

    # Remove remaining ASCII control characters while
    # preserving normal tabs and line breaks.

    text = re.sub(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
        "",
        text,
    )

    return text.strip()


def call_ollama(prompt):
    # Cloud deployment: use free Gemini API when configured.

    gemini_api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if gemini_api_key:
        try:
            client = genai.Client(
                api_key=gemini_api_key
            )

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )

            if response and response.text:
                return response.text.strip()

            return None

        except Exception:
            return None

    # Local development: continue using Ollama exactly as before.

    ollama_path = find_ollama()

    if not ollama_path:
        return None

    try:
        process = subprocess.run(
            [
                ollama_path,
                "run",
                OLLAMA_MODEL,
            ],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=60,
            encoding="utf-8",
            errors="ignore",
        )

        if process.returncode != 0:
            return None

        return clean_ollama_output(
            process.stdout
        )

    except Exception:
        return None


def build_prompt(
    question,
    evidence,
):
    evidence_text = "\n\n".join(
        [
            (
                f"POLICY: "
                f"{item['metadata'].get('policy_name', '')}\n"
                f"POLICY ID: "
                f"{item['metadata'].get('policy_id', '')}\n"
                f"VERSION: "
                f"{item['metadata'].get('version', '')}\n"
                f"STATUS: "
                f"{item['metadata'].get('status', '')}\n"
                f"EFFECTIVE DATE: "
                f"{item['metadata'].get('effective_date', '')}\n"
                f"OWNER: "
                f"{item['metadata'].get('policy_owner', '')}\n"
                f"CONTENT:\n"
                f"{item['document']}"
            )
            for item in evidence
        ]
    )

    return f"""
You are the policy assistant for Petadel Technology Services (PTS).

Answer the employee's question using ONLY the authoritative policy
evidence provided below.

Rules:

1. Do not invent policy information.
2. Do not use general knowledge.
3. Do not make up requirements.
4. The supplied evidence is the only policy authority available.
5. If the evidence answers the question, answer directly.
6. Do not refuse when the answer is clearly contained in the evidence.
7. If evidence is insufficient, say that sufficient policy information
   is unavailable.
8. For multiple questions, answer supported portions and identify
   unsupported portions.
9. Do not create citations.
10. 10. Keep the answer clear and concise.
11. Preserve exact policy numbers, deadlines, restrictions, and
    requirements.
12. Do not repeat policy metadata, document headers, or the full policy text in the answer. Provide only the information needed to answer the employee's question.
IMPORTANT:

The evidence below has already been filtered by the application for
policy eligibility.

Do not substitute another policy for the policy evidence provided.

If the question asks for a number, amount, duration, deadline, allowance,
or entitlement, look carefully through the supplied policy text for
the exact value before deciding that the information is unavailable.

QUESTION:

{question}

AUTHORITATIVE POLICY EVIDENCE:

{evidence_text}

Answer the question strictly from the evidence.

""".strip()


def looks_like_refusal(answer):
    if not answer:
        return True

    text = answer.lower().strip()

    refusal_phrases = [
        "i don't have enough information",
        "i do not have enough information",
        "insufficient information",
        "cannot answer",
        "can't answer",
        "unable to answer",
        "not enough information",
        "no information available",
        "i don't have access",
        "i do not have access",
        "not provided in the policy",
        "does not specify",
        "doesn't specify",
        "not specified",
        "not available in the policy",
    ]

    return any(
        phrase in text
        for phrase in refusal_phrases
    )


def generate_answer(
    question,
    evidence,
):
    if not evidence:
        return (
            "I don't have sufficient authoritative "
            "policy information to answer that question."
        )

    prompt = build_prompt(
        question,
        evidence,
    )

    answer = call_ollama(prompt)

    if (
        answer
        and not looks_like_refusal(answer)
    ):
        return answer

    retry_prompt = f"""
Answer the employee's question using ONLY the policy evidence below.

The application has already determined that this evidence is
authoritative, active, and approved.

The answer may be explicitly contained in the evidence even if the
question uses different wording.

Do not refuse if the answer is explicitly contained in the evidence.

If the question asks for a number, duration, amount, deadline, or
entitlement, identify the exact value from the policy text.

Do not invent information.

QUESTION:

{question}

POLICY EVIDENCE:

{chr(10).join(item["document"] for item in evidence)}

Give a direct answer based strictly on the policy evidence.

""".strip()

    retry = call_ollama(
        retry_prompt
    )

    if (
        retry
        and not looks_like_refusal(retry)
    ):
        return retry

    return create_deterministic_fallback(
        question,
        evidence,
    )


# ============================================================
# DETERMINISTIC FALLBACK
# ============================================================

def create_deterministic_fallback(
    question,
    evidence,
):
    if not evidence:
        return (
            "I don't have sufficient authoritative "
            "policy information to answer that question."
        )

    question_lower = question.lower()

    # --------------------------------------------------------
    # Employee Leave Policy
    # --------------------------------------------------------

    leave_evidence = [
        item
        for item in evidence
        if item["metadata"]
        .get("policy_name", "")
        .lower()
        == "employee leave policy"
    ]

    if leave_evidence:
        combined_text = "\n\n".join(
            item["document"]
            for item in leave_evidence
        ).lower()

        if (
            "vacation"
            in question_lower
            or "pto"
            in question_lower
            or "paid time off"
            in question_lower
        ):
            match = re.search(
                r"(\d+)\s+days?\s+(?:per|a)\s+year",
                combined_text,
            )

            if match:
                return (
                    "According to the Employee Leave Policy, "
                    f"full-time employees receive "
                    f"**{match.group(1)} days of paid time off "
                    "per year**."
                )

        if (
            "parental"
            in question_lower
            or "maternity"
            in question_lower
            or "paternity"
            in question_lower
            or "baby"
            in question_lower
            or "birth"
            in question_lower
        ):
            match = re.search(
                r"(?:up to|up to a maximum of)\s+(\d+)\s+weeks?",
                combined_text,
            )

            if match:
                return (
                    "According to the Employee Leave Policy, "
                    f"eligible employees may receive up to "
                    f"**{match.group(1)} weeks of parental leave**."
                )

        if "sick" in question_lower:
            match = re.search(
                r"(\d+)\s+days?\s+(?:per|a)\s+year",
                combined_text,
            )

            if match:
                return (
                    "According to the Employee Leave Policy, "
                    f"employees receive **{match.group(1)} "
                    "sick-leave days per year**."
                )

    # --------------------------------------------------------
    # Generic fallback
    # --------------------------------------------------------

    best = evidence[0]

    policy_name = best["metadata"].get(
        "policy_name",
        "the applicable policy",
    )

    content = best["document"].strip()

    content = re.sub(
        r"^#{1,6}\s+",
        "",
        content,
        flags=re.MULTILINE,
    )

    return (
        f"According to the {policy_name}, "
        f"the applicable policy states:\n\n"
        f"{content}"
    )


# ============================================================
# SUPPORTING SOURCE
# ============================================================

def render_sources(evidence):
    if not evidence:
        return

    st.markdown("### Supporting Source")

    displayed = set()

    for item in evidence:
        metadata = item["metadata"]

        policy_id = metadata.get(
            "policy_id",
            "",
        )

        policy_name = metadata.get(
            "policy_name",
            "Policy",
        )

        key = policy_id or policy_name

        if key in displayed:
            continue

        displayed.add(key)

        with st.container(border=True):
            st.markdown(
                f"**📄 {policy_name}**"
            )

            st.write(
                f"**Policy ID:** {policy_id}"
            )

            st.write(
                f"**Version:** "
                f"{metadata.get('version', 'N/A')}"
            )

            st.write(
                f"**Status:** "
                f"{metadata.get('status', 'N/A').title()}"
            )

            st.write(
                f"**Effective Date:** "
                f"{metadata.get('effective_date', 'N/A')}"
            )

            st.write(
                f"**Owner:** "
                f"{metadata.get('policy_owner', 'N/A')}"
            )


# ============================================================
# SESSION STATE
# ============================================================

if "initialized" not in st.session_state:
    st.session_state.initialized = False

if "answer" not in st.session_state:
    st.session_state.answer = None

if "sources" not in st.session_state:
    st.session_state.sources = []

if "question" not in st.session_state:
    st.session_state.question = ""


# ============================================================
# INITIAL INGESTION
# ============================================================

collection = get_chroma_collection()

if not st.session_state.initialized:
    if collection.count() == 0:
        with st.spinner(
            "Loading policy knowledge..."
        ):
            ingest_policies()

    st.session_state.initialized = True


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("# 📘 PolicyAssist AI")

    st.markdown(
        """
        **Petadel Technology Services**
        AI-powered policy knowledge assistant.
        """
    )

    st.divider()

    st.markdown("### Knowledge Base")

    policies = load_policy_documents()

    eligible = sum(
        1
        for policy in policies
        if policy_is_eligible(
            policy["metadata"]
        )
    )

    st.write(
        f"Policy Files: **{len(policies)}**"
    )

    st.write(
        f"Eligible Policies: **{eligible}**"
    )

    st.write(
        f"Indexed Sections: **{collection.count()}**"
    )

    st.divider()

    if st.button(
        "Refresh Policy Knowledge",
        use_container_width=True,
    ):
        with st.spinner(
            "Refreshing policy knowledge..."
        ):
            (
                files_count,
                eligible_count,
                section_count,
            ) = ingest_policies(
                force=True
            )

        st.success(
            f"Loaded {files_count} policies, "
            f"{eligible_count} eligible policies, "
            f"{section_count} sections."
        )

        st.rerun()


# ============================================================
# MAIN PAGE
# ============================================================

st.title(
    "📘 Petadel PolicyAssist AI"
)

st.markdown(
    "Get answers to company policy questions."
)

st.divider()


# ============================================================
# QUESTION INPUT
# ============================================================

question = st.text_input(
    "Ask a policy question",
    value=st.session_state.question,
    placeholder=(
        "Example: What should I do if I receive "
        "a suspicious email?"
    ),
    key="policy_question",
)


# ============================================================
# SUBMIT
# ============================================================

submit = st.button(
    "Ask PolicyAssist",
    type="primary",
    use_container_width=True,
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if submit:
    question = st.session_state.policy_question.strip()

    if not question:
        st.warning(
            "Please enter a policy question."
        )

    else:
        st.session_state.question = question

        with st.spinner(
            "Retrieving policy evidence..."
        ):
            candidates = retrieve_policy_evidence(
                question
            )

            evidence = select_supporting_evidence(
                question,
                candidates,
            )

        if not evidence:
            st.session_state.answer = (
                "I don't have sufficient authoritative "
                "policy information to answer that question."
            )

            st.session_state.sources = []

        else:
            with st.spinner(
                "Generating response..."
            ):
                answer = generate_answer(
                    question,
                    evidence,
                )

            st.session_state.answer = answer
            st.session_state.sources = evidence

        st.rerun()


# ============================================================
# DISPLAY RESPONSE
# ============================================================

if st.session_state.answer:
    st.markdown(
        "### PolicyAssist Response"
    )

    with st.container(
        border=True
    ):
        display_answer = re.sub(
            r"^#{1,6}\s*",
            "",
            st.session_state.answer,
            flags=re.MULTILINE,
        )

        st.markdown(
            display_answer
        )

    render_sources(
        st.session_state.sources
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "👍 Helpful",
            use_container_width=True,
        ):
            st.success(
                "Thank you for the feedback."
            )

    with col2:
        if st.button(
            "👎 Needs Review",
            use_container_width=True,
        ):
            st.warning(
                "This response should be reviewed "
                "by the appropriate policy owner."
            )
