"""Check which LinkedIn connections are already in the outreach DB."""
import sqlite3

db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()

names = [
    'Ely Kahn', 'Andreas Freund', 'Erick Antezana', 'Faisal ALFadialy',
    'Bandar Alqurashi', 'Aaron Bennett', 'Zeshan Saghir', 'Dawn Cappelli',
    'Andrew Penner', 'Douglas Jost', 'Kenneth Jones', 'Cory McNeley',
    'Craig Schmitz', 'Luis Bontempo', 'Nigel Gooding', 'Lucas Walter',
    'Dan McInerney', 'Richard Schaefer', 'Karl Mattson', 'Jean-Paul Mariton',
    'Phil Hamlin', 'Stephen Sammut', 'Christos Varsakelis', 'Tim Wedande',
    'Fleur Boos', 'Jerry Perullo', 'Tarek Ahmad', 'Brandon Harris',
    'Casey Fleming', 'John Bradley', 'Anand Shah', 'Steve Messina',
    'Andreea Manea', 'Michael Sinno', 'Ash Hunt', 'Jake Bernardes',
    'Lavy Stokhamer', 'Anas Basalamah', 'Iannis Drakos',
    'Gustavo Alves dos Santos', 'Doug Hubbard', 'Vincent Messina',
    'Anthony Wenger', 'Zahirudeen Premji', 'Berta Rodriguez-Hervas',
    'Anna Ibiteye', 'Das Venkatesan', 'Leo Cullen', 'Matt Schmid',
    'Khairul Azlan', 'Diana Spiridon', 'John Vander Weit',
    'Travis Lee', 'Tahnee Perry', 'Varun Chhibber', 'Shahruny Mohd Akil',
    'Nick Galbreath', 'Jerry Lamar'
]

print('=== IN DB ===')
found = []
for name in names:
    rows = cur.execute("""SELECT name, lane, channel, message_sent_at, signal_type, investor_score
        FROM prospects WHERE name LIKE ?""", ('%' + name + '%',)).fetchall()
    if rows:
        for r in rows:
            print('  {} | lane={} | ch={} | sent={} | signal={} | score={}'.format(
                r[0], r[1], r[2], r[3], r[4], r[5]))
            found.append(name)

print()
print('=== NOT IN DB ({}) ==='.format(len(names) - len(set(found))))
for name in names:
    if name not in found:
        print('  ' + name)

db.close()
