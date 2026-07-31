import unittest
import os
import sys
import json

# Python modül arama yoluna 'app' dizinini güvenle ekleme
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from saas_system_restore import SaaSSystemRestoreModule

class TestSaaSSystemRestore(unittest.TestCase):
    def setUp(self):
        self.restorer = SaaSSystemRestoreModule(base_dir="app")
        self.test_snapshot_dir = os.path.join("app", "backups", "snapshot_test_20260731")
        os.makedirs(self.test_snapshot_dir, exist_ok=True)
        
        metadata_path = os.path.join(self.test_snapshot_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump({"tenant_id": "tenant_alpha_01", "status": "secure"}, f)

    def test_invalid_auth_token(self):
        response = self.restorer.restore_latest_snapshot(
            target_tenant_id="tenant_alpha_01",
            auth_token="Invalid-Token",
            idempotency_key="key_001"
        )
        self.assertEqual(response["status"], "error")
        self.assertIn("Auth/JWT", response["message"])

    def test_tenant_isolation_violation(self):
        response = self.restorer.restore_latest_snapshot(
            target_tenant_id="tenant_hacker_99",
            auth_token="Bearer-CG-secrettoken123",
            idempotency_key="key_002"
        )
        self.assertEqual(response["status"], "error")
        self.assertIn("Tenant ID uyuşmazlığı", response["message"])

    def test_idempotency_protection(self):
        key = "unique_restore_key_777"
        self.restorer.restore_latest_snapshot(
            target_tenant_id="tenant_alpha_01",
            auth_token="Bearer-CG-secrettoken123",
            idempotency_key=key
        )
        response = self.restorer.restore_latest_snapshot(
            target_tenant_id="tenant_alpha_01",
            auth_token="Bearer-CG-secrettoken123",
            idempotency_key=key
        )
        self.assertEqual(response["status"], "error")
        self.assertIn("Mükerrer", response["message"])

if __name__ == "__main__":
    unittest.main()
