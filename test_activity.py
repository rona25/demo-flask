import time

from test import BaseTest


class ActivityTest(BaseTest):
    def test_activity_create(self):
        vendor_id = self.VENDOR_ID_SURFER

        status_code, data = self.post(
            '/1/vendor/%s/create_activity' % vendor_id,
            name='test activity - %s' % int(time.time())
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])

    def test_activity_delete(self):
        vendor_id = self.VENDOR_ID_SURFER

        # create a new activity
        status_code, data = self.post(
            '/1/vendor/%s/create_activity' % vendor_id,
            name='test activity - %s' % int(time.time())
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])
        activity_id = data['activity_id']

        # delete the newly-created activity
        status_code, data = self.post(
            '/1/vendor/%s/delete_activity' % vendor_id,
            activity_id=activity_id,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])

    def test_activity_delete_with_created_slots(self):
        vendor_id = self.VENDOR_ID_SURFER

        # create a new activity
        status_code, data = self.post(
            '/1/vendor/%s/create_activity' % vendor_id,
            name='forbidden activity - %s' % int(time.time())
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])
        activity_id = data['activity_id']

        # create a new slot for the activity
        status_code, data = self.post(
            '/1/activity/%s/create_slot' % activity_id,
            slot_num=1,
            date='2013-07-04',
            start_time='16:15',
            price=39999,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])
        slot_id = data['slot_id']

        # delete the newly-created activity
        status_code, data = self.post(
            '/1/vendor/%s/delete_activity' % vendor_id,
            activity_id=activity_id,
        )
        self.assertEqual(400, status_code)
        self.assertEqual(1, data['error_code'])

    def test_vendor_create_invalid(self):
        status_code, data = self.post(
            '/1/vendor/create',
            name='',
        )
        self.assertEqual(400, status_code)
        self.assertEqual(1, data['error_code'])

    def test_activity_available_days(self):
        activity_id = self.ACTIVITY_ID_SURF_LESSONS

        params = {
            'activity_id': activity_id,
            'from': '2013-10-14',
            'to': '2013-10-16',
        }
        status_code, data = self.get(
            '/1/activity/%(activity_id)s/available_days?from=%(from)s&to=%(to)s' % params,
        )
        self.assertEqual(200, status_code)
        self.assertTrue(data['data'])
        self.assertEqual(3, len(data['data']))
        self.assertEqual(
            [('2013-10-14', 1), ('2013-10-15', 4), ('2013-10-16', 1)],
            [(i['date'], i['count']) for i in data['data']]
        )

    def test_activity_available_times(self):
        activity_id = self.ACTIVITY_ID_SURF_LESSONS

        params = {
            'activity_id': activity_id,
            'date': '2013-10-31',
        }
        status_code, data = self.get(
            '/1/activity/%(activity_id)s/available_times?date=%(date)s' % params,
        )
        self.assertEqual(200, status_code)
        self.assertTrue(data['data'])
        self.assertEqual(3, len(data['data']))
        self.assertEqual(
            [('10:00:00', 1), ('12:00:00', 2), ('14:00:00', 1)],
            [(i['time'], i['count']) for i in data['data']]
        )

    def test_activity_create_and_delete_slot(self):
        activity_id = self.ACTIVITY_ID_SURF_LESSONS

        # create a new slot
        status_code, data = self.post(
            '/1/activity/%s/create_slot' % activity_id,
            slot_num=1,
            date='2013-06-05',
            start_time='11:30',
            end_time='12:30',
            price=7999,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])
        slot_id = data['slot_id']

        # verify the slot is available
        params = {
            'activity_id': activity_id,
            'from': '2013-06-05',
            'to': '2013-06-05',
        }
        status_code, data = self.get(
            '/1/activity/%(activity_id)s/available_slots?from=%(from)s&to=%(to)s' % params,
        )
        self.assertEqual(200, status_code)
        self.assertTrue(data['data'])
        self.assertEqual(1, len(data['data']))
        self.assertEqual(
            [slot_id],
            [i['slot_id'] for i in data['data']]
        )

        # delete the newly-created slot
        status_code, data = self.post(
            '/1/activity/%s/delete_slot' % activity_id,
            slot_id=slot_id,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])

        # verify the slot is no longer available
        params = {
            'activity_id': activity_id,
            'from': '2013-06-05',
            'to': '2013-06-05',
        }
        status_code, data = self.get(
            '/1/activity/%(activity_id)s/available_slots?from=%(from)s&to=%(to)s' % params,
        )
        self.assertEqual(200, status_code)
        self.assertFalse(data['data'])

    def test_activity_delete_booked_slot(self):
        activity_id = self.ACTIVITY_ID_SURF_LESSONS
        user_id = self.USER_ID_SOMEBODY

        # create a new slot
        status_code, data = self.post(
            '/1/activity/%s/create_slot' % activity_id,
            slot_num=1,
            date='2013-06-06',
            start_time='11:30',
            end_time='12:30',
            price=7999,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])
        slot_id = data['slot_id']

        # book the slot
        status_code, data = self.post(
            '/1/activity/%s/book' % activity_id,
            user_id=user_id,
            slot_id=slot_id,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])
        booking_id = data['booking_id']

        # try to delete the booked slot
        status_code, data = self.post(
            '/1/activity/%s/delete_slot' % activity_id,
            slot_id=slot_id,
        )
        self.assertEqual(400, status_code)
        self.assertEqual(1, data['error_code'])
