import firebird.driver as fdb

def get_connection():

    connection = fdb.connect(
        'localhost:/Users/anuragakp456/firebird_DB/transcript.fdb',
        user='SYSDBA',
        password='masterkey'  
    )

    return connection


#  Please create the table manually in your Firebird database using a database management tool or script.
        
        #     CREATE TABLE interview_transcripts (
        #         username VARCHAR(255) NOT NULL,
        #         role VARCHAR(20) NOT NULL,
        #         interview_id BIGINT NOT NULL,
        #         transcript VARCHAR(30000) NOT NULL,
        #         status VARCHAR(20) DEFAULT 'inprogress' NOT NULL,
        #         created_at TIMESTAMP DEFAULT CURRENT_TIME,
                
        #         CONSTRAINT chk_role4 CHECK (role IN ('candidate', 'panel', 'ai')),
        #         CONSTRAINT chk_status4 CHECK (status IN ('completed', 'inprogress'))
        #     );