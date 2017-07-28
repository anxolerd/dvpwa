CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  first_name TEXT NOT NULL,
  middle_name TEXT,
  last_name TEXT NOT NULL,
  username TEXT NOT NULL,
  pwd_hash TEXT NOT NULL,
  is_admin BOOLEAN DEFAULT FALSE
);
CREATE UNIQUE INDEX CONCURRENTLY ON users USING BTREE (username);

CREATE TABLE students (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);
CREATE INDEX CONCURRENTLY ON students USING BTREE (name);


CREATE TABLE courses (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT
);
CREATE UNIQUE INDEX CONCURRENTLY ON courses USING BTREE (title);


CREATE TABLE marks (
  id SERIAL PRIMARY KEY,
  date TIMESTAMP WITH TIME ZONE DEFAULT now(),
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  points INTEGER NOT NULL
);

ALTER TABLE marks ADD FOREIGN KEY (student_id) REFERENCES students(id);
ALTER TABLE marks ADD FOREIGN KEY (course_id) REFERENCES courses(id);

CREATE TABLE course_reviews (
  id SERIAL PRIMARY KEY,
  date TIMESTAMP WITH TIME ZONE DEFAULT now(),
  course_id INTEGER NOT NULL,
  review_text TEXT
);

ALTER TABLE course_reviews ADD FOREIGN KEY (course_id) REFERENCES courses (id);
