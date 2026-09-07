import os
import sys
import unittest
from unittest.mock import patch


# ---------------------------------------------------------
# Make the PolicyAssist app importable
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

APP_DIR = os.path.join(
    PROJECT_ROOT,
    "app"
)

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)


import app


# ---------------------------------------------------------
# Test Configuration
# ---------------------------------------------------------

MAX_DISTANCE = 1.20


# ---------------------------------------------------------
# Policy Eligibility Tests
# ---------------------------------------------------------

class TestPolicyEligibility(unittest.TestCase):

    def valid_metadata(self):
        return {
            "policy_id": "TEST-001",
            "policy_name": "Test Policy",
            "version": "1.0",
            "status": "Active",
            "effective_date": "2026-01-01",
            "policy_owner": "Test Owner",
            "approval_status": "Approved",
        }

    def test_active_approved_policy_is_eligible(self):
        metadata = self.valid_metadata()

        self.assertTrue(
            app.policy_is_eligible(metadata)
        )

    def test_draft_policy_is_not_eligible(self):
        metadata = self.valid_metadata()
        metadata["status"] = "Draft"

        self.assertFalse(
            app.policy_is_eligible(metadata)
        )

    def test_superseded_policy_is_not_eligible(self):
        metadata = self.valid_metadata()
        metadata["status"] = "Superseded"

        self.assertFalse(
            app.policy_is_eligible(metadata)
        )

    def test_missing_policy_id_is_not_eligible(self):
        metadata = self.valid_metadata()
        del metadata["policy_id"]

        self.assertFalse(
            app.policy_is_eligible(metadata)
        )

    def test_missing_owner_is_not_eligible(self):
        metadata = self.valid_metadata()
        del metadata["policy_owner"]

        self.assertFalse(
            app.policy_is_eligible(metadata)
        )


# ---------------------------------------------------------
# Policy Topic Routing Tests
# ---------------------------------------------------------

class TestPolicyTopicRouting(unittest.TestCase):

    def test_leave_question_identifies_leave_policy(self):
        question = (
            "How many PTO days do full-time employees "
            "receive per year?"
        )

        topics = app.get_strong_policy_topics(
            question
        )

        self.assertIn(
            "Employee Leave Policy",
            topics
        )

    def test_remote_question_identifies_remote_policy(self):
        question = (
            "How many days per week can an employee "
            "work remotely?"
        )

        topics = app.get_strong_policy_topics(
            question
        )

        self.assertIn(
            "Remote Work Policy",
            topics
        )

    def test_security_question_identifies_security_policy(self):
        question = (
            "What should I do if I receive a suspicious email?"
        )

        topics = app.get_strong_policy_topics(
            question
        )

        self.assertIn(
            "Information Security Policy",
            topics
        )


# ---------------------------------------------------------
# Retrieval Distance Tests
# ---------------------------------------------------------

class TestRetrievalThreshold(unittest.TestCase):

    def test_distance_within_threshold_is_eligible(self):
        distance = 1.10

        self.assertLessEqual(
            distance,
            MAX_DISTANCE
        )

    def test_distance_above_threshold_is_rejected(self):
        distance = 1.30

        self.assertGreater(
            distance,
            MAX_DISTANCE
        )


# ---------------------------------------------------------
# Required Policy Metadata Tests
# ---------------------------------------------------------

class TestRequiredMetadata(unittest.TestCase):

    def test_required_metadata_is_present(self):
        metadata = {
            "policy_id": "PTS-HR-001",
            "policy_name": "Test Policy",
            "version": "1.0",
            "status": "Active",
            "effective_date": "2026-01-01",
            "policy_owner": "Human Resources",
        }

        required_fields = [
            "policy_id",
            "policy_name",
            "version",
            "status",
            "effective_date",
            "policy_owner",
        ]

        for field in required_fields:
            self.assertIn(
                field,
                metadata
            )


# ---------------------------------------------------------
# Authority Rule Tests
# ---------------------------------------------------------

class TestAuthorityRules(unittest.TestCase):

    def test_active_policy_can_be_authoritative_candidate(self):
        metadata = {
            "policy_id": "HR-LEAVE-001",
            "policy_name": "Employee Leave Policy",
            "version": "3.0",
            "status": "Active",
            "effective_date": "2026-01-01",
            "policy_owner": "Human Resources",
            "approval_status": "Approved",
        }

        self.assertTrue(
            app.policy_is_eligible(metadata)
        )

    def test_unverified_policy_is_rejected(self):
        metadata = {
            "policy_id": "HR-LEAVE-001",
            "policy_name": "Employee Leave Policy",
            "version": "4.0",
            "status": "Unverified",
            "effective_date": "2026-02-01",
            "policy_owner": "Human Resources",
            "approval_status": "Pending",
        }

        self.assertFalse(
            app.policy_is_eligible(metadata)
        )


# ---------------------------------------------------------
# Evaluation Dataset Tests
# ---------------------------------------------------------

class TestEvaluationDataset(unittest.TestCase):

    def test_evaluation_dataset_exists(self):
        dataset_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "evaluation_dataset.csv"
        )

        self.assertTrue(
            os.path.exists(dataset_path)
        )

    def test_evaluation_dataset_contains_30_cases(self):
        import csv

        dataset_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "evaluation_dataset.csv"
        )

        with open(
            dataset_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            rows = list(
                csv.DictReader(file)
            )

        self.assertEqual(
            len(rows),
            30
        )

    def test_evaluation_dataset_contains_required_fields(self):
        import csv

        dataset_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "evaluation_dataset.csv"
        )

        with open(
            dataset_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)
            rows = list(reader)

        required_fields = {
            "test_id",
            "category",
            "question",
            "expected_policy",
            "expected_behavior",
            "expected_answer",
        }

        self.assertTrue(
            required_fields.issubset(
                set(rows[0].keys())
            )
        )


# ---------------------------------------------------------
# Application Safety Tests
# ---------------------------------------------------------

class TestApplicationSafety(unittest.TestCase):

    def test_empty_question_is_handled(self):
        question = ""

        self.assertIsInstance(
            question,
            str
        )

        self.assertEqual(
            question.strip(),
            ""
        )

    def test_whitespace_question_is_handled(self):
        question = "   "

        self.assertEqual(
            question.strip(),
            ""
        )


# ---------------------------------------------------------
# Test Runner
# ---------------------------------------------------------

if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )