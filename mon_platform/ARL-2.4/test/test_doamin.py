import unittest
from app import services
from app.config import Config

class TestDomain(unittest.TestCase):
    def test_altdns(self):
        c =  ['www.baidu.com', 'map.baidu.com', 'test.baidu.com']
        w =['private', 'api-docs', 'lc']

        data = services.altdns(c, "baidu.com", w)
        self.assertTrue(len(data) >= 1)

    def test_mass_dns(self):
        data = services.mass_dns("tophant.com", ["www"])
        self.assertTrue(len(data) >= 1)

if __name__ == '__main__':
    unittest.main()
