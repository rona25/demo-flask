from test import BaseTest


class BookingTest(BaseTest):

    def test_activity_available_slots_one_day(self):
        activity_id = self.ACTIVITY_ID_SURF_LESSONS

        data = self.get_single_day_activity_slots(activity_id)
        self.assertTrue(data['data'])
        self.assertEqual(4, data['total'])
        self.assertEqual([302, 303, 304, 305], [i['slot_id'] for i in data['data']])

    def test_activity_available_slots_date_range(self):
        activity_id = self.ACTIVITY_ID_SURF_LESSONS

        params = {
            'activity_id': activity_id,
            'from': '2013-10-14',
            'to': '2013-10-16',
        }
        status_code, data = self.get(
            '/1/activity/%(activity_id)s/available_slots?from=%(from)s&to=%(to)s' % params,
        )
        self.assertEqual(200, status_code)
        self.assertTrue(data['data'])
        self.assertEqual(6, data['total'])
        self.assertEqual([301, 302, 303, 304, 305, 306], [i['slot_id'] for i in data['data']])

    def test_activity_booking(self):
        activity_id = self.ACTIVITY_ID_SURF_LESSONS
        user_id = self.USER_ID_SOMEBODY
        slot_id_to_be_booked = 304

        # make sure the slots are not booked
        data = self.get_single_day_activity_slots(activity_id)
        self.assertTrue(data['data'])
        self.assertEqual([302, 303, 304, 305], [i['slot_id'] for i in data['data']])

        # book one of the slots
        status_code, data = self.post(
            '/1/activity/%s/book' % activity_id,
            user_id=user_id,
            slot_id=slot_id_to_be_booked,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])
        booking_id = data['booking_id']

        # verify that the booked slot is no longer available
        data = self.get_single_day_activity_slots(activity_id)
        self.assertTrue(data['data'])
        self.assertEqual(3, data['total'])
        self.assertEqual([302, 303, 305], [i['slot_id'] for i in data['data']])

        # try to book the same slot
        status_code, data = self.post(
            '/1/activity/%s/book' % activity_id,
            user_id=user_id,
            slot_id=slot_id_to_be_booked,
        )
        self.assertEqual(400, status_code)
        self.assertEqual(1, data['error_code'])

        # delete the booking
        status_code, data = self.post(
            '/1/activity/%s/delete_booking' % activity_id,
            user_id=user_id,
            booking_id=booking_id,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])

        # make sure the slot is now available once again
        data = self.get_single_day_activity_slots(activity_id)
        self.assertTrue(data['data'])
        self.assertEqual([302, 303, 304, 305], [i['slot_id'] for i in data['data']])


    def test_activity_booking_duplicates(self):
        activity_id = self.ACTIVITY_ID_SURF_LESSONS
        user_id = self.USER_ID_SOMEBODY
        slot_id_to_be_booked = 301
        booking_date = '2013-10-14'

        # make sure the slots are not booked
        data = self.get_single_day_activity_slots(activity_id, date=booking_date)
        self.assertTrue(data['data'])
        self.assertEqual([slot_id_to_be_booked], [i['slot_id'] for i in data['data']])

        # book one of the slots
        status_code, data = self.post(
            '/1/activity/%s/book' % activity_id,
            user_id=user_id,
            slot_id=slot_id_to_be_booked,
        )
        self.assertEqual(200, status_code)
        self.assertEqual(0, data['error_code'])
        booking_id = data['booking_id']

        # verify that the booked slot is no longer available
        data = self.get_single_day_activity_slots(activity_id, date=booking_date)
        self.assertFalse(data['data'])
        self.assertEqual(0, data['total'])
