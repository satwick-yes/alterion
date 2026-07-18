import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from actions.free_apis_router import free_api_query
from core.integration_gateway import integration_gateway

class TestFreeApisRouter(unittest.TestCase):

    def test_integration_gateway_permissions(self):
        print("\n--- Running Integration Gateway free_api_query Permission Test ---")
        # Ensure free_api_query tool is allowed for any companion
        self.assertTrue(integration_gateway.verify_tool_permission("System & Control", "free_api_query"))
        self.assertTrue(integration_gateway.verify_tool_permission("Research & Intelligence", "free_api_query"))
        self.assertTrue(integration_gateway.verify_tool_permission("Developer Core", "free_api_query"))
        print("[PASS] free_api_query is permitted for all companions.")

    def test_free_api_query_missing_description(self):
        print("\n--- Running free_api_query Missing Parameter Test ---")
        res = free_api_query(parameters={})
        self.assertIn("missing", res.lower())
        print("[PASS] Missing parameter validation works.")

if __name__ == "__main__":
    unittest.main()
