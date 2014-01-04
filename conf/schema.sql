/**
 initialization
 */
CREATE DATABASE IF NOT EXISTS demo;
USE demo;

/**
 model
 */
CREATE TABLE IF NOT EXISTS activity (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    vendor_id BIGINT UNSIGNED NOT NULL REFERENCES vendor(id),
    name VARCHAR(255) NOT NULL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_name (name)
) ENGINE=innodb;

CREATE TABLE IF NOT EXISTS activity_recurring (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    activity_id BIGINT UNSIGNED NOT NULL,
    num_slots INT UNSIGNED NOT NULL,
    scheduling_start_date DATE NOT NULL,
    scheduling_end_date DATE NOT NULL,
    recurring_schedule INT UNSIGNED NOT NULL,
    activity_start_time TIME NOT NULL,
    activity_end_time TIME DEFAULT NULL,
    price_cents INT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    KEY idx_activity_date_time (activity_id, scheduling_start_date, activity_start_time)
) ENGINE=innodb;

CREATE TABLE IF NOT EXISTS activity_slot (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    activity_id BIGINT UNSIGNED NOT NULL,
    activity_date DATE NOT NULL,
    activity_start_time TIME NOT NULL,
    slot_num INT UNSIGNED NOT NULL,
    price_cents INT UNSIGNED NOT NULL,
    activity_end_time TIME DEFAULT NULL,
    recurring_id BIGINT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uniq_activity_slot (activity_id, activity_date, activity_start_time, slot_num),
    KEY idx_all_activity_date_time (activity_date, activity_start_time)
) ENGINE=innodb;

CREATE TABLE IF NOT EXISTS booking (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    activity_slot_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uniq_booking (activity_slot_id),
    KEY idx_user_id (user_id, ts),
    KEY idx_ts (ts)
) ENGINE=innodb;

CREATE TABLE IF NOT EXISTS user (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(255),
    PRIMARY KEY (id),
    KEY idx_name (name)
) ENGINE=innodb;

CREATE TABLE IF NOT EXISTS vendor (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(255),
    PRIMARY KEY (id),
    KEY idx_name (name)
) ENGINE=innodb;

/**
 constraints
 */
ALTER TABLE activity ADD CONSTRAINT fk_activiy_vendor_id
    FOREIGN KEY (vendor_id) REFERENCES vendor(id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT;

ALTER TABLE activity_recurring ADD CONSTRAINT fk_activity_recurring_activity_id
    FOREIGN KEY (activity_id) REFERENCES activity(id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT;

ALTER TABLE activity_slot ADD CONSTRAINT fk_activity_slot_activity_id
    FOREIGN KEY (activity_id) REFERENCES activity(id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT;
ALTER TABLE activity_slot ADD CONSTRAINT fk_activity_slot_recurring_id
    FOREIGN KEY (recurring_id) REFERENCES activity_recurring(id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT;

ALTER TABLE booking ADD CONSTRAINT fk_booking_user_id
    FOREIGN KEY (user_id) REFERENCES user(id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT;
ALTER TABLE booking ADD CONSTRAINT fk_booking_activity_slot
    FOREIGN KEY (activity_slot_id) REFERENCES activity_slot(id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT;

ALTER TABLE activity AUTO_INCREMENT = 1000;
ALTER TABLE activity_recurring AUTO_INCREMENT = 1000;
ALTER TABLE activity_slot AUTO_INCREMENT = 1000;
ALTER TABLE booking AUTO_INCREMENT = 1000;
ALTER TABLE user AUTO_INCREMENT = 1000;
ALTER TABLE vendor AUTO_INCREMENT = 1000;
