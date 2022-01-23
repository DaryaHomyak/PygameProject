import sqlite3
con = sqlite3.connect("Race project")
cur = con.cursor()
result = cur.execute("""SELECT * FROM car_icons ORDER BY price""").fetchall()
cur.execute("UPDATE car_icons SET status = 'lock' ")
cur.execute("UPDATE car_icons SET status = 'choosed' WHERE name = 'стартовую машину' ")
cur.execute('''UPDATE progress SET coins = 15000 ''')
print('Прогресс:')
for a in cur.execute("""SELECT * FROM progress""").fetchall():
    print(a)
print("Машинки:")
result = cur.execute("""SELECT * FROM car_icons ORDER BY price""").fetchall()
for r in result:
    print(r)
con.commit()
con.close()