-- Basic server configuration
admins = { "admin@localhost" }

-- Enable modules
modules_enabled = {
    -- Required modules
    "roster";           -- Allow users to have a roster
    "saslauth";        -- Authentication for clients and servers
    "tls";             -- Add support for secure TLS on c2s/s2s connections
    "dialback";        -- s2s dialback support
    "disco";           -- Service discovery
    "posix";           -- POSIX functionality, sends server to background
    
    -- Optional modules
    "ping";            -- Replies to XMPP pings with pongs
    "register";        -- Allow users to register on this server
    "bosh";            -- Enable BOSH clients, aka "Jabber over HTTP"
    "websocket";       -- Enable WebSocket support
    "http_files";      -- Serve static files from a directory over HTTP
}

-- HTTPS/SSL configuration
https_ports = { 5281 }
https_interfaces = { "*" }

ssl = {
    key = "/etc/prosody/certs/localhost.key";
    certificate = "/etc/prosody/certs/localhost.crt";
}

-- Authentication configuration
authentication = "internal_plain"

-- Logging configuration
log = {
    info = "/var/log/prosody/prosody.log";
    error = "/var/log/prosody/error.log";
    debug = "/var/log/prosody/debug.log";
}

-- Module path configuration
plugin_paths = { "/usr/lib/prosody-modules" }

-- Network settings
interfaces = { "*" }
network_backend = "epoll"

-- HTTP/BOSH configuration
http_ports = { 5280 }
http_interfaces = { "*" }
consider_bosh_secure = true

-- Virtual hosts
VirtualHost "localhost"
    enabled = true
    authentication = "internal_plain"
    
    -- TLS configuration
    ssl = {
        key = "/etc/prosody/certs/localhost.key";
        certificate = "/etc/prosody/certs/localhost.crt";
    }

-- Components
Component "conference.localhost" "muc"
    name = "Conference Service"

-- Cross-domain communication
cross_domain_websocket = true
cross_domain_bosh = true

-- For testing/development only - disable in production
allow_unencrypted_plain_auth = true
c2s_require_encryption = false
s2s_require_encryption = false
