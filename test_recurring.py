from test import BaseTest

class RecurringActivityTest(BaseTest):
    def test_generate_recurring_slots(self):
        activity_id = self.ACTIVITY_ID_SURF_LESSONS
        recurring_activity_id = self.RECURRING_ID_EVERY_MONDAY_AT_5P

        # create a new slot
        status_code, data = self.post(
            '/1/activity/%s/generate_recurring_slots' % activity_id,
            recurring_id=recurring_activity_id,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])
        self.assertEqual(11, data['total'])

        # verify the slot is available
        params = {
            'activity_id': activity_id,
            'from': '2014-10-01',
            'to': '2015-01-01',
        }
        status_code, data = self.get(
            '/1/activity/%(activity_id)s/available_days?from=%(from)s&to=%(to)s' % params,
        )
        self.assertEqual(200, status_code)
        self.assertTrue(data['data'])
        self.assertEqual(11, len(data['data']))
        self.assertEqual(
            [
                ('2014-10-20', 1),
                ('2014-10-27', 1),
                ('2014-11-03', 1),
                ('2014-11-10', 1),
                ('2014-11-17', 1),
                ('2014-11-24', 1),
                ('2014-12-01', 1),
                ('2014-12-08', 1),
                ('2014-12-15', 1),
                ('2014-12-22', 1),
                ('2014-12-29', 1),
            ],
            [(i['date'], i['count']) for i in data['data']]
        )

