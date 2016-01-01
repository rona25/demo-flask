import datetime
import logging
import os
import pymysql

from flask import Flask, jsonify, request


app = Flask(__name__)
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user=os.environ['MYSQL_USER'],
    passwd=os.environ['MYSQL_PWD'],
    db='demo',
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('demo')


@app.route('/1/vendor', methods=['GET'])
def vendors():
    data = []
    num_total = 0
    try:
        cur = conn.cursor()
        num_total = cur.execute('SELECT id, name FROM vendor ORDER BY id') or 0
        for row in cur.fetchall():
            data.append(dict(
                id=row[0],
                name=row[1],
            ))

    except Exception, e:
        error = str(e)
        log.error(error, exc_info=1)

    ctx = {
        'total': num_total,
        'data': data,
    }
    return jsonify(error_code=0, **ctx)


@app.route('/1/vendor/create', methods=['POST'])
def vendor_create():
    error = None
    vendor_id = None

    try:
        vendor_name = request.form.get('name')

        if not vendor_name:
            raise StandardError('"name" is required')

        cur = conn.cursor()
        cur.execute('INSERT INTO vendor (name) VALUES (%s)', args=(vendor_name))
        vendor_id = conn.insert_id()
        conn.commit()

    except Exception, e:
        error = str(e)
        conn.rollback()
        log.error(error, exc_info=1)

    if error:
        return jsonify(error_code=1, error=error), 400
    else:
        return jsonify(error_code=0, id=vendor_id)


@app.route('/1/vendor/<int:vendor_id>', methods=['GET'])
def vendor_details(vendor_id):
    error = None
    vendor = {}
    try:
        cur = conn.cursor()
        cur.execute('SELECT id, name FROM vendor WHERE id = %s', args=(vendor_id)) or 0
        row = cur.fetchone()
        if row:
            vendor = dict(
                id=row[0],
                name=row[1],
            )

    except Exception, e:
        error = str(e)
        log.error(error, exc_info=1)

    if error:
        return jsonify(error=error), 400
    elif vendor:
        return jsonify(**vendor)
    else:
        return jsonify(), 404


@app.route('/1/vendor/<int:vendor_id>/activities', methods=['GET'])
def vendor_activities(vendor_id):
    error = None
    data = []
    num_total = 0
    try:
        sql = 'SELECT id, name, ts FROM activity WHERE vendor_id = %s ORDER BY id'

        cur = conn.cursor()
        num_total = cur.execute(sql, args=(vendor_id)) or 0
        for row in cur.fetchall():
            data.append(dict(
                id=row[0],
                name=row[1],
                timestamp=row[2],
            ))

    except Exception, e:
        error = str(e)
        log.error(error, exc_info=1)

    if error:
        return jsonify(error=error), 400
    else:
        return jsonify(data=data, total=num_total)


@app.route('/1/vendor/<int:vendor_id>/create_activity', methods=['POST'])
def activity_create(vendor_id):
    error = None
    activity_id = None

    try:
        activity_name = request.form.get('name')

        if not activity_name:
            raise StandardError('"name "is required')

        sql = 'INSERT INTO activity (vendor_id, name) VALUES (%s, %s)'
        cur = conn.cursor()
        cur.execute(sql, args=(vendor_id, activity_name))
        activity_id = conn.insert_id()
        conn.commit()

    except Exception, e:
        error = str(e)
        conn.rollback()
        log.error(error, exc_info=1)

    if error:
        return jsonify(error_code=1, error=error), 400
    else:
        return jsonify(error_code=0, activity_id=activity_id)


@app.route('/1/vendor/<int:vendor_id>/delete_activity', methods=['POST'])
def activity_delete(vendor_id):
    error = None

    try:
        activity_id = request.form.get('activity_id')

        if not activity_id:
            raise StandardError('"activity_id" is required')

        cur = conn.cursor()
        cur.execute('SELECT vendor_id FROM activity WHERE id = %s', args=(activity_id))
        data = cur.fetchone()
        if not data or data[0] != vendor_id:
            raise StandardError('unexpected vendor id')

        sql = 'DELETE FROM activity WHERE id = %s'
        cur = conn.cursor()
        cur.execute(sql, args=(activity_id))
        conn.commit()

    except Exception, e:
        error = str(e)
        conn.rollback()
        log.error(error, exc_info=1)

    if error:
        return jsonify(error_code=1, error=error), 400
    else:
        return jsonify(error_code=0)


@app.route('/1/activity/<int:activity_id>/available_days', methods=['GET'])
def activity_available_days(activity_id):
    error = None
    data = []
    num_total = 0
    try:
        from_date = request.args.get('from')
        to_date = request.args.get('to')

        if not (from_date and to_date):
            if from_date:
                to_date = '2050-12-31'
            elif to_date:
                from_date = '1970-01-01'
            else:
                raise ValueError('"from" or "to" date not specified')

        cur = conn.cursor()
        sql = '''
            SELECT s.activity_date, COUNT(1) AS cnt
            FROM activity_slot s
            LEFT JOIN booking b ON b.activity_slot_id = s.id
            WHERE s.activity_id = %s
            AND b.activity_slot_id IS NULL
            AND s.activity_date BETWEEN %s AND %s
            GROUP BY s.activity_date
            ORDER BY s.activity_date
        '''
        num_total = cur.execute(sql, args=(activity_id, from_date, to_date)) or 0
        for row in cur.fetchall():
            data.append(dict(
                date=str(row[0]),
                count=row[1],
            ))

    except Exception, e:
        error = str(e)
        log.error(error, exc_info=1)

    if error:
        return jsonify(error=error), 400
    else:
        return jsonify(data=data, total=num_total)


@app.route('/1/activity/<int:activity_id>/available_times', methods=['GET'])
def activity_available_times(activity_id):
    error = None
    data = []
    num_total = 0
    try:
        activity_date = request.args.get('date')

        if not activity_date:
            raise ValueError('"date" not specified')

        cur = conn.cursor()
        sql = '''
            SELECT s.activity_start_time, COUNT(1) AS cnt
            FROM activity_slot s
            LEFT JOIN booking b ON b.activity_slot_id = s.id
            WHERE s.activity_id = %s
            AND s.activity_date = %s
            AND b.activity_slot_id IS NULL
            GROUP BY s.activity_start_time
            ORDER BY s.activity_start_time
        '''
        num_total = cur.execute(sql, args=(activity_id, activity_date)) or 0
        for row in cur.fetchall():
            data.append(dict(
                time=str(row[0]),
                count=row[1],
            ))

    except Exception, e:
        error = str(e)
        log.error(error, exc_info=1)

    if error:
        return jsonify(error=error), 400
    else:
        return jsonify(data=data, total=num_total)


@app.route('/1/activity/<int:activity_id>/available_slots', methods=['GET'])
def activity_available_slots(activity_id):
    error = None
    data = []
    num_total = 0
    try:
        from_date = request.args.get('from')
        to_date = request.args.get('to')

        if not (from_date and to_date):
            if from_date:
                to_date = '2050-12-31'
            elif to_date:
                from_date = '1970-01-01'
            else:
                raise ValueError('"from" or "to" date not specified')

        cur = conn.cursor()
        sql = '''
            SELECT s.id, s.activity_id, s.activity_date, s.activity_start_time, s.price_cents, s.slot_num
            FROM activity_slot s
            LEFT JOIN booking b ON b.activity_slot_id = s.id
            WHERE s.activity_id = %s
            AND b.activity_slot_id IS NULL
            AND s.activity_date BETWEEN %s AND %s
        '''
        num_total = cur.execute(sql, args=(activity_id, from_date, to_date)) or 0
        for row in cur.fetchall():
            data.append(dict(
                slot_id=row[0],
                activity_id=row[1],
                date=str(row[2]),
                time=str(row[3]),
                price=row[4],
            ))

    except Exception, e:
        error = str(e)
        log.error(error, exc_info=1)

    if error:
        return jsonify(error=error), 400
    else:
        return jsonify(data=data, total=num_total)


@app.route('/1/activity/<int:activity_id>/book', methods=['POST'])
def activity_slot_booking(activity_id):
    error = None
    booking_id = None

    try:
        activity_slot_id = request.form.get('slot_id')
        booking_user_id = request.form.get('user_id')

        if not activity_slot_id:
            raise StandardError('"slot_id" is required')
        if not booking_user_id:
            raise StandardError('"user_id" is required')

        cur = conn.cursor()
        cur.execute('SELECT activity_id FROM activity_slot WHERE id = %s', args=(activity_slot_id))
        data = cur.fetchone()
        if not data or data[0] != activity_id:
            raise StandardError('unexpected activity id')

        sql = '''
            INSERT INTO booking (activity_slot_id, user_id) VALUES (%s, %s)
        '''
        cur.execute(sql, args=(activity_slot_id, booking_user_id))
        booking_id = conn.insert_id()
        conn.commit()

    except Exception, e:
        error = str(e)
        conn.rollback()
        log.error(error, exc_info=1)

    if error:
        return jsonify(error_code=1, error=error), 400
    else:
        return jsonify(error_code=0, booking_id=booking_id)


@app.route('/1/activity/<int:activity_id>/create_slot', methods=['POST'])
def activity_slot_create(activity_id):
    error = None
    slot_id = None

    try:
        slot_num = request.form.get('slot_num')
        slot_date = request.form.get('date')
        slot_start_time = request.form.get('start_time')
        slot_end_time = request.form.get('end_time')
        price = request.form.get('price')

        if not slot_num:
            raise StandardError('"slot_num" is required')
        if not slot_date:
            raise StandardError('"date" is required')
        if not slot_start_time:
            raise StandardError('"start_time" is required')
        if not price:
            raise StandardError('"price" is required')

        sql = '''
            INSERT INTO activity_slot
            (activity_id, activity_date, activity_start_time, slot_num, price_cents, activity_end_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        cur = conn.cursor()
        cur.execute(
            sql,
            args=(activity_id, slot_date, slot_start_time, slot_num, price, slot_end_time)
        )
        slot_id = conn.insert_id()
        conn.commit()

    except Exception, e:
        error = str(e)
        conn.rollback()
        log.error(error, exc_info=1)

    if error:
        return jsonify(error_code=1, error=error), 400
    else:
        return jsonify(error_code=0, slot_id=slot_id)


@app.route('/1/activity/<int:activity_id>/delete_slot', methods=['POST'])
def activity_slot_delete(activity_id):
    error = None

    try:
        slot_id = request.form.get('slot_id')

        if not slot_id:
            raise StandardError('"slot_id" is required')

        cur = conn.cursor()
        cur.execute('SELECT activity_id FROM activity_slot WHERE id = %s', args=(slot_id))
        data = cur.fetchone()
        if not data or data[0] != activity_id:
            raise StandardError('unexpected activity id')

        sql = '''
            DELETE FROM activity_slot WHERE id = %s
        '''
        cur = conn.cursor()
        cur.execute(sql, args=(slot_id))
        conn.commit()

    except Exception, e:
        error = str(e)
        conn.rollback()
        log.error(error, exc_info=1)

    if error:
        return jsonify(error_code=1, error=error), 400
    else:
        return jsonify(error_code=0, slot_id=slot_id)


@app.route('/1/activity/<int:activity_id>/delete_booking', methods=['POST'])
def activity_slot_delete_booking(activity_id):
    error = None

    try:
        booking_id = request.form.get('booking_id')

        if not booking_id:
            raise StandardError('"booking_id" is required')

        sql = '''
            SELECT s.activity_id
            FROM booking b
            INNER JOIN activity_slot s ON b.activity_slot_id = s.id
            WHERE b.id = %s
        '''
        cur = conn.cursor()
        cur.execute(sql, args=(booking_id))
        data = cur.fetchone()
        if not data or data[0] != activity_id:
            raise StandardError('unexpected activity slot id')

        sql = '''
            DELETE FROM booking WHERE id = %s
        '''
        cur = conn.cursor()
        cur.execute(sql, args=(booking_id))
        conn.commit()

    except Exception, e:
        error = str(e)
        conn.rollback()
        log.error(error, exc_info=1)

    if error:
        return jsonify(error_code=1, error=error), 400
    else:
        return jsonify(error_code=0)


@app.route('/1/activity/<int:activity_id>/generate_recurring_slots', methods=['POST'])
def activity_slot_generate_recurring_slots(activity_id):
    error = None
    num_created = 0

    try:
        recurring_activity_id = request.form.get('recurring_id')

        if not recurring_activity_id:
            raise StandardError('"recurring_id" is required')

        sql = '''
            SELECT id, activity_id, num_slots, scheduling_start_date, scheduling_end_date,
                recurring_schedule, activity_start_time, activity_end_time, price_cents
            FROM activity_recurring
            WHERE id = %s
        '''
        cur = conn.cursor()
        cur.execute(sql, args=(recurring_activity_id))
        data = cur.fetchone()
        if not data:
            raise StandardError('recurring activity info not found')

        recurring_activity_id = data[0]
        num_slots = data[2]
        start_date = data[3]
        end_date = data[4]
        schedule_info = data[5]
        activity_start_time = data[6]
        activity_end_time = data[7]
        activity_price = data[8]

        if not (end_date and end_date >= start_date):
            raise StandardError('recurring end date not valid')
        elif data[1] != activity_id:
            raise StandardError('unexpected activity id')

        # the scheduling pattern is comprised of 3 bytes:
        #   * first byte:   each bit represents the repeating day (1=mon, 7=sun)
        #   * second byte:  the week to repeat -- 1 == repeat every week; 2 == repeat every other week
        recurring_day = schedule_info % 8    # 1st byte = 1:mon - 7:sun
        repeat_weeks = schedule_info >> 8    # 2nd byte = repeat every weeks
        if not recurring_day:
            raise StandardError('recurring day not set')
        elif not repeat_weeks:
            raise StandardError('recurring repeat weeks not set')

        # determine the first date in the specified window
        if start_date.isoweekday() != recurring_day:
            if start_date.isoweekday() < recurring_day:
                start_date = start_date + datetime.timedelta(days=recurring_day - start_date.isoweekday())
            else:
                start_date = start_date + datetime.timedelta(days=7 - (start_date.isoweekday() - recurring_day))

        sql = '''
            INSERT INTO activity_slot
            (activity_id, activity_date, activity_start_time, slot_num,
                price_cents, activity_end_time, recurring_id) VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        '''
        values = []
        while start_date < end_date:
            for slot in xrange(1, num_slots + 1):
                values.append((
                    activity_id,
                    start_date,
                    activity_start_time,
                    slot,
                    activity_price,
                    activity_end_time,
                    recurring_activity_id,
                ))

            start_date = start_date + datetime.timedelta(weeks=repeat_weeks)

        cur = conn.cursor()
        num_created = cur.executemany(sql, args=values)
        conn.commit()

    except Exception, e:
        error = str(e)
        conn.rollback()
        log.error(error, exc_info=1)

    if error:
        return jsonify(error_code=1, error=error), 400
    else:
        return jsonify(error_code=0, total=num_created)


if __name__ == "__main__":
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5555,
    )
