import unittest
from waste_sorter.decision import Item, Decision, Gate, assess

class PolicyTests(unittest.TestCase):
    def test_examples(self):
        paper = Item('cardboard', .95, 'paper')
        plastic = Item('plastic', .95, 'recycling')
        can = Item('can', .95, 'recycling')
        unknown = Item('unknown', .42)
        cases = [([plastic], 'READY', 'recycling'),
                 ([paper, paper], 'READY', 'paper'),
                 ([plastic, can], 'READY', 'recycling'),
                 ([paper, plastic], 'ERROR_MIXED_WASTE', None),
                 ([unknown], 'UNSURE', 'general'),
                 ([plastic, unknown], 'UNSURE', 'general'),
                 ([paper, plastic, unknown], 'ERROR_MIXED_WASTE', None)]
        for items, status, category in cases:
            with self.subTest(status=status, items=items):
                result = assess(items, True, False, .8)
                self.assertEqual((result.status, result.category), (status, category))

    def test_detection_and_special_streams(self):
        self.assertEqual(assess([], True, True, .8).status, 'EMPTY')
        self.assertEqual(assess([], False, False, .8).status, 'WARNING_DETECTION')
        self.assertEqual(assess([Item('battery', .95, unsupported=True)], True, False, .8).status, 'ERROR_UNSUPPORTED')
        self.assertEqual(assess([Item('unknown', .4)], False, False, .8).status, 'WARNING_DETECTION')

    def test_threshold_is_configurable(self):
        obj = [Item('paper', .75, 'paper')]
        self.assertEqual(assess(obj, True, False, .8).status, 'UNSURE')
        self.assertEqual(assess(obj, True, False, .7).status, 'READY')

class TemporalTests(unittest.TestCase):
    def setUp(self):
        self.g = Gate(dict(stable_frames=2, stable_seconds=.5,
                           max_gap_seconds=2, empty_reset_seconds=1))

    def test_fresh_recheck_latch_and_empty_reset(self):
        d = Decision('UNSURE', 'general')
        self.assertIsNone(self.g.update(d, 'batch', 0)[1])
        self.assertIsNone(self.g.update(d, 'batch', .6)[1])
        self.assertEqual(self.g.update(d, 'batch', .8)[1], 'general')
        self.assertIsNone(self.g.update(d, 'batch', 1)[1])
        self.g.update(Decision('EMPTY'), (), 1.1)
        self.g.update(Decision('EMPTY'), (), 2.2)
        self.assertFalse(self.g.latched)

    def test_change_or_veto_cancels_pending_event(self):
        d = Decision('READY', 'paper')
        self.g.update(d, 'batch', 0)
        self.g.update(d, 'batch', .6)
        self.assertIsNone(self.g.update(d, 'changed', .8)[1])
        self.g.update(Decision('ERROR_MIXED_WASTE'), 'changed', 1)
        self.assertIsNone(self.g.update(d, 'changed', 1.2)[1])

    def test_fault_requires_clearance(self):
        self.g.fault()
        for t in [0, .6, .8]:
            self.assertIsNone(self.g.update(Decision('READY', 'paper'), 'batch', t)[1])

if __name__ == '__main__':
    unittest.main()
