import sqlite3

def create_huge_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS STUDENT")
    cursor.execute("CREATE TABLE STUDENT(NAME TEXT, COURSE TEXT, SECTION TEXT, MARKS INTEGER)")
    
    students = [
        ('John', 'Data Science', 'A', 88), ('Alice', 'AI', 'B', 92),
        ('Bob', 'Data Science', 'A', 75), ('Charlie', 'Web Dev', 'C', 80),
        ('Diana', 'AI', 'B', 95), ('Ethan', 'Data Science', 'A', 62),
        ('Fiona', 'Web Dev', 'C', 89), ('George', 'AI', 'B', 77),
        ('Hannah', 'Data Science', 'A', 91), ('Ian', 'Web Dev', 'C', 55),
        ('Jenna', 'AI', 'B', 83), ('Kevin', 'Data Science', 'A', 70),
        ('Liam', 'Web Dev', 'C', 99), ('Mia', 'AI', 'B', 68),
        ('Noah', 'Data Science', 'A', 82), ('Olivia', 'Web Dev', 'C', 74),
        ('Pippa', 'AI', 'B', 90), ('Quinn', 'Data Science', 'A', 85),
        ('Ryan', 'Web Dev', 'C', 60), ('Sara', 'AI', 'B', 98)
    ]
    
    cursor.executemany("INSERT INTO STUDENT VALUES (?,?,?,?)", students)
    conn.commit()
    conn.close()
    print("database.db created")

if __name__ == "__main__":
    create_huge_db()