import time

from test import BaseTest


class VendorTest(BaseTest):
    def test_vendor_surfer(self):
        vendor_id = self.VENDOR_ID_SURFER
        vendor_name = 'Joe the Surf Instructor'

        status_code, data = self.get(
            '/1/vendor/%s' % vendor_id,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(vendor_id, data['id'])
        self.assertEqual(vendor_name, data['name'])

    def test_vendor_create_valid(self):
        vendor_name = 'foo bar bas - %s' % int(time.time())

        status_code, data = self.post(
            '/1/vendor/create',
            name=vendor_name,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])
        vendor_id = data['id']

        status_code, data = self.get(
            '/1/vendor/%s' % vendor_id,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(vendor_id, data['id'])
        self.assertEqual(vendor_name, data['name'])

    def test_vendor_create_invalid(self):
        status_code, data = self.post(
            '/1/vendor/create',
            name='',
        )
        self.assertEqual(400, status_code)
        self.assertEqual(1, data['error_code'])


