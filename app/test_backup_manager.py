import unittest
from saas_backup_manager import SaaSBackupManager

class TestSaaSBackupManager(unittest.TestCase):
    def setUp(self):
        self.manager = SaaSBackupManager(base_dir="app")

    def test_successful_backup(self):
        response = self.manager.create_secure_snapshot(
            tenant_id="tenant_test_01",
            auth_token="Bearer-CG-secrettoken123",
            idempotency_key="test_key_100"
        )
        self.assertEqual(response["status"], "success")

    def test_idempotency_protection(self):
        self.manager.create_secure_snapshot(
            tenant_id="tenant_test_01",
            auth_token="Bearer-CG-secrettoken123",
            idempotency_key="test_key_200"
        )
        duplicate_response = self.manager.create_secure_snapshot(
            tenant_id="tenant_test_01",
            auth_token="Bearer-CG-secrettoken123",
            idempotency_key="test_key_200"
        )
        self.assertEqual(duplicate_response["status"], "error")

if __name__ == "__main__":
    unittest.main()
