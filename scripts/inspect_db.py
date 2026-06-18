import sqlite3

def main():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'inventario_%'")
        print('Tables:', cur.fetchall())

        cur.execute('SELECT codigo, COUNT(*) FROM inventario_materiaprima GROUP BY codigo ORDER BY COUNT(*) DESC LIMIT 20')
        dupes = cur.fetchall()
        print('Top duplicate counts (codigo, count):')
        for d in dupes:
            print(d)

        print('\nSample rows:')
        cur.execute('SELECT id, codigo, nombre FROM inventario_materiaprima ORDER BY id LIMIT 50')
        for r in cur.fetchall():
            print(r)
    except Exception as e:
        print('ERROR:', e)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
