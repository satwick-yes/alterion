import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.inference_wrapper import inference_client

class TestMoaConsensus(unittest.TestCase):

    def test_moa_consensus_execution(self):
        print("\n--- Running MoA Consensus Query Test ---")
        prompt = "Provide a one-sentence definition of cloud computing."
        
        # Run consensus search
        result = inference_client.generate_consensus_text(
            prompt=prompt,
            system_instruction="Keep the definition clear and concise."
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 10)
        self.assertIn("cloud", result.lower() + " " + "computing")
        print(f"[PASS] Consensus result retrieved: {result.encode('ascii', 'ignore').decode('ascii')}")

if __name__ == "__main__":
    unittest.main()
