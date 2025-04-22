-- Create the database
CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    course VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    profile_pic VARCHAR(255) DEFAULT 'default.png',
    address TEXT,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (roll_no)
);

-- Create attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Late') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (student_id, date)
);

-- Create subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    course VARCHAR(50) NOT NULL,
    UNIQUE KEY unique_subject_course (name, course)
);

-- Create marks table
CREATE TABLE IF NOT EXISTS marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    exam_type VARCHAR(50) NOT NULL,
    marks FLOAT NOT NULL,
    max_marks FLOAT NOT NULL,
    exam_date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Create fees table
CREATE TABLE IF NOT EXISTS fees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    fee_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status ENUM('Paid', 'Pending', 'Partial') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Insert some sample subjects
INSERT INTO subjects (name, course) VALUES 
('Database Management Systems', 'Computer Science'),
('Data Structures', 'Computer Science'),
('Object Oriented Programming', 'Computer Science'),
('Computer Networks', 'Computer Science'),
('Algorithms', 'Computer Science'),
('Operating Systems', 'Computer Science'),
('Web Development', 'Computer Science'),
('Machine Learning', 'Computer Science');

-- Insert some sample students
INSERT INTO students (name, roll_no, course, year, email, phone, address) VALUES
('Rahul Sharma', 'CS2023001', 'Computer Science', 2, 'rahul.sharma@example.com', '9876543210', '123 Main Street, Delhi'),
('Priya Patel', 'CS2023002', 'Computer Science', 2, 'priya.patel@example.com', '8765432109', '456 Park Avenue, Mumbai'),
('Amit Kumar', 'CS2023003', 'Computer Science', 3, 'amit.kumar@example.com', '7654321098', '789 Lake Road, Bangalore'),
('Sneha Singh', 'CS2023004', 'Computer Science', 1, 'sneha.singh@example.com', '6543210987', '321 River View, Chennai'),
('Vikram Mehta', 'CS2023005', 'Computer Science', 4, 'vikram.mehta@example.com', '5432109876', '654 Hill Street, Hyderabad');