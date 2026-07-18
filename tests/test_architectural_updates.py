import unittest
import os
import sys
import shutil
import tempfile
import json
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.inference_wrapper import inference_client
from agent.orchestrator import semantic_router
from agent.state_manager import state_manager, TaskState, AgentState
from agent.multi_agent import multi_agent_framework
from memory.vector_memory import vector_memory_db
from core.integration_gateway import integration_gateway

class TestArchitecturalUpdates(unittest.TestCase):
    
    def test_1_inference_wrapper(self):
        print("\n--- Running Inference Wrapper Tests ---")
        self.assertIsNotNone(inference_client)
        
        # Test mock embedding generation (either API or fallback)
        emb = inference_client.generate_embedding("Test embedding text statement.")
        self.assertEqual(len(emb), 768)
        print("[PASS] Inference Wrapper Embedding test passed.")

    def test_2_semantic_router(self):
        print("\n--- Running Semantic Router Tests ---")
        # Route a system-like task
        comp1 = semantic_router.route_intent("please open Brave browser and clean my desktop")
        self.assertEqual(comp1.name, "System & Control")
        
        # Route a research-like task
        comp2 = semantic_router.route_intent("what are the latest trends in quantum computing?")
        self.assertEqual(comp2.name, "Research & Intelligence")
        
        # Route a developer-like task
        comp3 = semantic_router.route_intent("write a python script to parse logs and run it")
        self.assertEqual(comp3.name, "Developer Core")
        
        print("[PASS] Semantic Router routing test passed.")

    def test_3_vector_memory(self):
        print("\n--- Running Vector Memory Tests ---")
        # Save memory statement
        test_fact = "Tony's favorite hobby is building robotic arm components."
        vector_memory_db.add_memory(test_fact, "preferences")
        
        # Search memory
        matches = vector_memory_db.search_memories("What does Tony like to build in his free time?", limit=1)
        self.assertTrue(len(matches) > 0)
        self.assertIn("robotic arm", matches[0]["text"])
        print("[PASS] Vector Memory add/search test passed.")

    def test_4_multi_agent_framework(self):
        print("\n--- Running Multi-Agent Framework Tests ---")
        goal = "Research three local coffee shops and list their menu items"
        companion = semantic_router.companions["research"]
        
        # Test complex task decomposition
        workers = multi_agent_framework.decompose_task("test-task-123", goal, companion)
        self.assertTrue(len(workers) > 0)
        for w in workers:
            self.assertEqual(w.task_id, "test-task-123")
            self.assertIsNotNone(w.role)
            self.assertIsNotNone(w.instruction)
            self.assertIsNotNone(w.tool)
        print(f"[PASS] Decomposed task into {len(workers)} bots successfully.")

    def test_5_integration_gateway(self):
        print("\n--- Running Integration Gateway Tests ---")
        # Validate authorized tool
        system_perm = integration_gateway.verify_tool_permission("System & Control", "open_app")
        self.assertTrue(system_perm)
        
        # Validate unauthorized tool
        bad_perm = integration_gateway.verify_tool_permission("Communication", "system_shell")
        self.assertFalse(bad_perm)
        
        # Test simulated OAuth execution
        response = integration_gateway.execute_oauth_api_call("gmail", "send_email", {"to": "test@test.com"})
        self.assertEqual(response["status"], "success")
        print("[PASS] Integration Gateway permissions and OAuth test passed.")

if __name__ == "__main__":
    unittest.main()
