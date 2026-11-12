import unittest
from job_agent.scoring import score_job, experience_requirement, salary_below_target

class ScoringTests(unittest.TestCase):
    def test_role_and_skills_raise_score(self):
        job = {"title": "Junior DevOps Engineer", "description": "AWS Linux Kubernetes Terraform CI/CD monitoring", "location": "India Remote", "company": "Example", "salary_text": None}
        profile = {"skills": ["AWS", "Linux", "Kubernetes", "Terraform"], "preferred_locations": ["India"], "years_experience": 1}
        score, reasons, warnings, matched, years = score_job(job, profile)
        self.assertGreaterEqual(score, 70)
        self.assertIn("AWS", matched)
    def test_experience_extraction(self):
        self.assertEqual(experience_requirement("Requires 3-5 years of experience"), 5)
    def test_salary_in_lpa(self):
        self.assertTrue(salary_below_target("4-5 LPA", 6))
        self.assertFalse(salary_below_target("USD 100,000", 6))

if __name__ == "__main__":
    unittest.main()
