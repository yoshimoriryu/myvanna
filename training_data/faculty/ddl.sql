CREATE TABLE faculty (
    faculty_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(100),
    title VARCHAR(100),
    hire_date DATE
);

CREATE TABLE publications (
    publication_id INT PRIMARY KEY,
    title TEXT NOT NULL,
    author_id INT,
    journal_name VARCHAR(255),
    publication_year INT,
    citation_count INT,
    FOREIGN KEY (author_id) REFERENCES faculty(faculty_id)
);