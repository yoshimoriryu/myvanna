-- Table to store information about academic staff
CREATE TABLE faculty (
    faculty_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(100),
    title VARCHAR(100), -- e.g., 'Professor', 'Associate Professor', 'Lecturer'
    hire_date DATE
);

-- Table to store information about research publications
CREATE TABLE publications (
    publication_id INT PRIMARY KEY,
    title TEXT NOT NULL,
    author_id INT, -- Foreign key linking to the faculty member who wrote it
    journal_name VARCHAR(255),
    publication_year INT,
    citation_count INT,
    FOREIGN KEY (author_id) REFERENCES faculty(faculty_id)
);