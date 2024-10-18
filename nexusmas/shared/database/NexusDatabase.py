import os
import json
import logging

logger = logging.getLogger(__name__)
class NexusDatabase():
    def __init__(self, *args, **kwargs):
        connection_string = kwargs.pop("connection_string", os.environ["NEXUS_DATABASE_URL"])

        # super().__init__(connection_string=connection_string, session_id=session_id, table_name='messages', *args, **kwargs)

        import psycopg
        from psycopg.rows import dict_row

        try:
            self.connection_string = connection_string
            self.connection = psycopg.connect(connection_string)
            self.cursor = self.connection.cursor(row_factory=dict_row)
            self.bootstrap()
        except psycopg.OperationalError as error:
            logger.error("ERROR initializing NexusDatabase object")
            logger.error(error)
        pass

    def bootstrap(self) -> None:
        self._create_users_table_if_not_exists()
        self._create_sessions_table_if_not_exists()
        # self._create_messages_table_if_not_exists()

    def _create_users_table_if_not_exists(self) -> None:
        create_users_table_query = """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            jabber_id VARCHAR(255) NOT NULL UNIQUE,
            nickname VARCHAR(255),
            role VARCHAR(255),
            email VARCHAR(255) UNIQUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );"""
        self.cursor.execute(create_users_table_query)
        self.connection.commit()

    def _create_sessions_table_if_not_exists(self) -> None:
        create_sessions_table_query = """CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            zep_session_id UUID DEFAULT gen_random_uuid(),
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );"""
        self.cursor.execute(create_sessions_table_query)

        create_session_user_table_query = """CREATE TABLE IF NOT EXISTS session_users (
            id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES sessions(id),
            user_id INTEGER REFERENCES users(id)
        );"""
        self.cursor.execute(create_session_user_table_query)

        self.connection.commit()

    # This is defined in langchain.memory.chat_message_histories.postgres
    # def _create_messages_table_if_not_exists(self) -> None:
    #     from pprint import pprint
    #     create_messages_table_query = """CREATE TABLE IF NOT EXISTS messages (
    #         id SERIAL PRIMARY KEY,
    #         session_id INTEGER NOT NULL REFERENCES sessions(id),
    #         user_id INTEGER REFERENCES users(id),
    #         type VARCHAR(255) CHECK (type IN ('human', 'ai', 'system')),
    #         content JSONB NOT NULL,
    #         created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    #     );"""
    #     self.cursor.execute(create_messages_table_query)
    #     self.connection.commit()

    def query(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def insert(self, query, params):
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.fetchone()

    def __del__(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def _create_user(self, user: dict) -> None:
        # lowercase jabber_id
        user["jabber_id"] = user["jabber_id"].lower()
        result = self.insert("""
            INSERT INTO users (jabber_id) VALUES (%s)
            RETURNING id;
        """, (user["jabber_id"],))
        from pprint import pprint
        print("_create_user")
        pprint(result)
        return result

    def get_user(self, jabber_id):
        query = "SELECT * FROM users WHERE jabber_id = %s;"
        # make jabber_id lowercase
        jabber_id = jabber_id.lower()

        result = self.query(query, (jabber_id,))
        if len(result) == 0:
            self._create_user({
                "jabber_id": jabber_id 
            })
            result = self.query(query, (jabber_id,))
            user = result[0]
        else:
            user = result[0]
        return user

    def get_summary_by_source_location(self, source_location):
        query = "SELECT summary FROM summaries WHERE source_location = %s ORDER BY version DESC LIMIT 1;"
        result = self.query(query, (source_location,))
        if len(result) == 0:
            return None
        return result[0]["summary"]

    def get_summary_by_checksum(self, checksum):
        query = "SELECT summary FROM summaries WHERE source_checksum = %s ORDER BY version DESC LIMIT 1;"
        result = self.query(query, (checksum,))
        if len(result) == 0:
            return None
        return result[0]["summary"]


    def insert_summary(self, source_location, source_checksum, summary):
        # summary has the following fields:
        # - source_location
        # - source_checksum
        # - summary
        # - version

        new_version = 1
        # Get the current version
        query = "SELECT version FROM summaries WHERE source_location = %s ORDER BY version DESC LIMIT 1;"
        result = self.query(query, (source_location,))
        if len(result) > 0:
            new_version = result[0]["version"] + 1

        query = "INSERT INTO summaries (source_location, source_checksum, summary, version) VALUES (%s, %s, %s, %s) RETURNING summary_id;"
        result = self.insert(query, (source_location, source_checksum, summary, new_version))
        return result