import firebird.driver as fdb

def get_connection():

    connection = fdb.connect(
        'localhost:/Users/Apple/firebird_db_files/transcript.fdb',
        user='SYSDBA',
        password='masterkey'  
    )
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE interview_transcripts (
                username VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                interview_id BIGINT NOT NULL,
                transcript VARCHAR(30000) NOT NULL,
                status VARCHAR(20) DEFAULT 'inprogress' NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIME,
                
                CONSTRAINT chk_role4 CHECK (role IN ('candidate', 'panel', 'ai')),
                CONSTRAINT chk_status4 CHECK (status IN ('completed', 'inprogress'))
            )
        """)
        
        connection.commit()
        print("Table created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    return connection
