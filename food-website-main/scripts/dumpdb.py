import sqlite3

conn = sqlite3.connect('database/testdb.db')
cursor = conn.cursor()


with open('database_dump.sql', 'w') as dump_file:
    for line in conn.iterdump():
        dump_file.write('%s\n' % line)

# Close the database connection
conn.close()