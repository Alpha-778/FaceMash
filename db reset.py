import psycopg2


def main():
    conn = psycopg2.connect('postgres://avnadmin:AVNS_w8Ct71HRTpe6brtEfgJ@servicesite-credit-system-114.l.aivencloud.com:20178/defaultdb?sslmode=require')

    query_sql = 'DROP TABLE IF EXISTS votes; CREATE TABLE votes (id SERIAL PRIMARY KEY,choice VARCHAR(10),image_name VARCHAR,user_id VARCHAR,created_at TIMESTAMP DEFAULT NOW());'
    # query_sql="Drop Table votes"
    cur = conn.cursor()
    cur.execute(query_sql)

    print("Done")


if __name__ == "__main__":
    main()