import os
import pytest
import psycopg2
import redis
import pika
import aioxmpp
import asyncio
import logging
import ssl

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_postgres_connection():
    """Test PostgreSQL connectivity"""
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get('POSTGRES_DB', 'nexusmas'),
            user=os.environ.get('POSTGRES_USER', 'nexusmas'),
            password=os.environ.get('POSTGRES_PASSWORD', 'nexusmas'),
            host=os.environ.get('POSTGRES_HOST', 'postgres')
        )
        assert conn.status == psycopg2.extensions.STATUS_READY
        logger.info("Successfully connected to PostgreSQL")
        conn.close()
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        raise

def test_redis_connection():
    """Test Redis connectivity"""
    try:
        r = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'redis'),
            port=6379,
            decode_responses=True
        )
        assert r.ping()
        logger.info("Successfully connected to Redis")
        r.close()
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise

def test_rabbitmq_connection():
    """Test RabbitMQ connectivity"""
    try:
        credentials = pika.PlainCredentials(
            username=os.environ.get('RABBITMQ_DEFAULT_USER', 'nexusmas'),
            password=os.environ.get('RABBITMQ_DEFAULT_PASS', 'nexusmas')
        )
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.environ.get('RABBITMQ_HOST', 'rabbitmq'),
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5
            )
        )
        assert connection.is_open
        logger.info("Successfully connected to RabbitMQ")
        connection.close()
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_xmpp_connection():
    """Test XMPP connectivity"""
    try:
        # Get XMPP host and port
        xmpp_host = os.environ.get('XMPP_HOST', 'prosody')
        xmpp_port = int(os.environ.get('XMPP_PORT', '5222'))
        
        # Create JID for test user - use localhost as domain since that's what prosody is configured for
        jid = aioxmpp.JID.fromstr("nexusmas@localhost")
        password = "nexusmas"
        
        # Create security layer with no TLS verification for testing
        security_layer = aioxmpp.security_layer.make(
            password,
            no_verify=True,
            ssl_context_factory=None,
            anonymous=True
        )
        
        # Create client with proper security layer
        client = aioxmpp.PresenceManagedClient(
            jid,
            security_layer,
            override_peer=[
                ("localhost", xmpp_host, xmpp_port)
            ]
        )
        
        async with client.connected() as stream:
            # Wait briefly to ensure connection is established
            await asyncio.sleep(1)
            
            # Verify stream is running
            assert stream.running
            
            # Set and verify presence
            presence = aioxmpp.PresenceState(available=True)
            client.presence = presence
            
            # Wait briefly for presence to be processed
            await asyncio.sleep(1)
            
            # Verify presence was set
            assert client.presence.available is True
            
            logger.info("Successfully connected to XMPP server and verified presence")
            
    except Exception as e:
        logger.error(f"Failed to connect to XMPP server: {str(e)}")
        raise

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
