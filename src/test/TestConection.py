import unittest

class TestConection(unittest.TestCase):
    pass

if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestConection)

    unittest.TextTestRunner(verbosity=2).run(suite)
