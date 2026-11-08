import unittest
from proficiency_comment import render, is_context

class Assessment(unittest.TestCase):
    def setUp(self):
        self.report={'overall_level':5,'overall_score':60.07,'level_scores':{str(i):{'name':str(i),'file_count':n} for i,n in enumerate([1,3,97,23,8,0,0,0],1)},'recommendations':['🔍 Detected AI tools: header','Fleet','Beads','Workflows','Other']}
    def test_metrics_and_native_order(self):
        text=render(self.report,[])
        self.assertIn('60.1/100',text)
        self.assertIn('132 context files',text)
        self.assertIn('1. Fleet\n2. Beads\n3. Workflows',text)
        self.assertNotIn('4. Other',text)
    def test_artifact_boundaries(self):
        self.assertTrue(is_context('docs/chain.md'))
        self.assertFalse(is_context('.entire/metadata/prompt.txt'))
    def test_added_acknowledgment(self):
        self.assertIn('adds context artifacts',render(self.report,[{'filename':'AGENTS.md','status':'added'}]))
    def test_removed_does_not_claim_positive_addition(self):
        text=render(self.report,[{'filename':'AGENTS.md','status':'removed'}])
        self.assertNotIn('adds context artifacts',text)
        self.assertIn('`AGENTS.md`: removed',text)
    def test_invalid_level(self):
        self.report['overall_level']=9
        with self.assertRaises(ValueError):render(self.report,[])
if __name__=='__main__':unittest.main()
