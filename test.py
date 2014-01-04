import json
import pymysql
import unittest

import main

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='demo')


class BaseTest(unittest.TestCase):
    VENDOR_ID_SURFER = 100
    ACTIVITY_ID_SURF_LESSONS = 200
    RECURRING_ID_EVERY_MONDAY_AT_5P = 400
    USER_ID_SOMEBODY = 900
    USER_ID_ANOTHER_ONE = 901

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()

    def setUp(self):
        super(BaseTest, self).setUp()
        self.app = main.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.db_conn = conn

        cur = self.db_conn.cursor()
        cur.execute('DELETE FROM booking')
        cur.execute('DELETE FROM activity_slot WHERE id >= 1000')
        cur.execute('DELETE FROM activity WHERE id >= 1000')
        self.db_conn.commit()

    def post(self, uri, **kwargs):
        result = self.client.post(
            uri,
            follow_redirects=True,
            data=dict(**kwargs)
        )
        return result.status_code, json.loads(result.data)

    def get(self, uri, **kwargs):
        args = dict(**kwargs)

        result = self.client.get(
            uri,
            follow_redirects=True,
            data=args
        )
        return result.status_code, json.loads(result.data)

    def get_single_day_activity_slots(self, activity_id, date=None):
        if not date:
            date = '2013-10-15'

        params = {
            'activity_id': activity_id,
            'from': date,
            'to': date,
        }
        status_code, data = self.get(
            '/1/activity/%(activity_id)s/available_slots?from=%(from)s&to=%(to)s' % params,
        )
        self.assertEqual(200, status_code)
        return data
