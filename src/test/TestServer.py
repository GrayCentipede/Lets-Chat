import unittest

class TestServer(unittest.TestCase):
    pass

if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestServer)

    unittest.TextTestRunner(verbosity=2).run(suite)
