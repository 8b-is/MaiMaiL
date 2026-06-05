#!/usr/bin/env bash
# _modules/scripts/new_options.sh
# THIS SCRIPT IS DESIGNED TO BE RUNNING BY MAILCOW SCRIPTS ONLY!
# DO NOT, AGAIN, NOT TRY TO RUN THIS SCRIPT STANDALONE!!!!!!

adapt_new_options() {

  CONFIG_ARRAY=(
  "AUTODISCOVER_SAN"
  "SKIP_LETS_ENCRYPT"
  "SKIP_SOGO"
  "USE_WATCHDOG"
  "WATCHDOG_NOTIFY_EMAIL"
  "WATCHDOG_NOTIFY_WEBHOOK"
  "WATCHDOG_NOTIFY_WEBHOOK_BODY"
  "WATCHDOG_NOTIFY_BAN"
  "WATCHDOG_NOTIFY_START"
  "WATCHDOG_EXTERNAL_CHECKS"
  "WATCHDOG_SUBJECT"
  "SKIP_CLAMD"
  "SKIP_OLEFY"
  "SKIP_IP_CHECK"
  "ADDITIONAL_SAN"
  "DOVEADM_PORT"
  "IPV4_NETWORK"
  "IPV6_NETWORK"
  "LOG_LINES"
  "SNAT_TO_SOURCE"
  "SNAT6_TO_SOURCE"
  "COMPOSE_PROJECT_NAME"
  "DOCKER_COMPOSE_VERSION"
  "SQL_PORT"
  "API_KEY"
  "API_KEY_READ_ONLY"
  "API_ALLOW_FROM"
  "MAILDIR_GC_TIME"
  "MAILDIR_SUB"
  "ACL_ANYONE"
  "FTS_HEAP"
  "FTS_PROCS"
  "SKIP_FTS"
  "ENABLE_SSL_SNI"
  "ALLOW_ADMIN_EMAIL_LOGIN"
  "SKIP_HTTP_VERIFICATION"
  "SOGO_EXPIRE_SESSION"
  "SOGO_URL_ENCRYPTION_KEY"
  "REDIS_PORT"
  "REDISPASS"
  "DOVECOT_MASTER_USER"
  "DOVECOT_MASTER_PASS"
  "MAILCOW_PASS_SCHEME"
  "ADDITIONAL_SERVER_NAMES"
  "WATCHDOG_VERBOSE"
  "WEBAUTHN_ONLY_TRUSTED_VENDORS"
  "SPAMHAUS_DQS_KEY"
  "SKIP_UNBOUND_HEALTHCHECK"
  "DISABLE_NETFILTER_ISOLATION_RULE"
  "HTTP_REDIRECT"
  "ENABLE_IPV6"
  )

  sed -i --follow-symlinks '$a\' maimail.conf
  for option in ${CONFIG_ARRAY[@]}; do
    if grep -q "${option}" maimail.conf; then
      continue
    fi

    echo "Adding new option \"${option}\" to maimail.conf"

    case "${option}" in
        AUTODISCOVER_SAN)
            echo '# Obtain certificates for autodiscover.* and autoconfig.* domains.' >> maimail.conf
            echo '# This can be useful to switch off in case you are in a scenario where a reverse proxy already handles those.' >> maimail.conf
            echo '# There are mixed scenarios where ports 80,443 are occupied and you do not want to share certs' >> maimail.conf
            echo '# between services. So acme-maimail obtains for maildomains and all web-things get handled' >> maimail.conf
            echo '# in the reverse proxy.' >> maimail.conf
            echo 'AUTODISCOVER_SAN=y' >> maimail.conf
            ;;

        DOCKER_COMPOSE_VERSION)
            echo "# Used Docker Compose version" >> maimail.conf
            echo "# Switch here between native (compose plugin) and standalone" >> maimail.conf
            echo "# For more informations take a look at the maimail docs regarding the configuration options." >> maimail.conf
            echo "# Normally this should be untouched but if you decided to use either of those you can switch it manually here." >> maimail.conf
            echo "# Please be aware that at least one of those variants should be installed on your machine or maimail will fail." >> maimail.conf
            echo "" >> maimail.conf
            echo "DOCKER_COMPOSE_VERSION=${DOCKER_COMPOSE_VERSION}" >> maimail.conf
            ;;

        DOVEADM_PORT)
            echo "DOVEADM_PORT=127.0.0.1:19991" >> maimail.conf
            ;;

        LOG_LINES)
            echo '# Max log lines per service to keep in Redis logs' >> maimail.conf
            echo "LOG_LINES=9999" >> maimail.conf
            ;;
        IPV4_NETWORK)
            echo '# Internal IPv4 /24 subnet, format n.n.n. (expands to n.n.n.0/24)' >> maimail.conf
            echo "IPV4_NETWORK=172.22.1" >> maimail.conf
            ;;
        IPV6_NETWORK)
            echo '# Internal IPv6 subnet in fc00::/7' >> maimail.conf
            echo "IPV6_NETWORK=fd4d:6169:6c63:6f77::/64" >> maimail.conf
            ;;
        SQL_PORT)
            echo '# Bind SQL to 127.0.0.1 on port 13306' >> maimail.conf
            echo "SQL_PORT=127.0.0.1:13306" >> maimail.conf
            ;;
        API_KEY)
            echo '# Create or override API key for web UI' >> maimail.conf
            echo "#API_KEY=" >> maimail.conf
            ;;
        API_KEY_READ_ONLY)
            echo '# Create or override read-only API key for web UI' >> maimail.conf
            echo "#API_KEY_READ_ONLY=" >> maimail.conf
            ;;
        API_ALLOW_FROM)
            echo '# Must be set for API_KEY to be active' >> maimail.conf
            echo '# IPs only, no networks (networks can be set via UI)' >> maimail.conf
            echo "#API_ALLOW_FROM=" >> maimail.conf
            ;;
        SNAT_TO_SOURCE)
            echo '# Use this IPv4 for outgoing connections (SNAT)' >> maimail.conf
            echo "#SNAT_TO_SOURCE=" >> maimail.conf
            ;;
        SNAT6_TO_SOURCE)
            echo '# Use this IPv6 for outgoing connections (SNAT)' >> maimail.conf
            echo "#SNAT6_TO_SOURCE=" >> maimail.conf
            ;;
        MAILDIR_GC_TIME)
            echo '# Garbage collector cleanup' >> maimail.conf
            echo '# Deleted domains and mailboxes are moved to /var/vmail/_garbage/timestamp_sanitizedstring' >> maimail.conf
            echo '# How long should objects remain in the garbage until they are being deleted? (value in minutes)' >> maimail.conf
            echo '# Check interval is hourly' >> maimail.conf
            echo 'MAILDIR_GC_TIME=1440' >> maimail.conf
            ;;
        ACL_ANYONE)
            echo '# Set this to "allow" to enable the anyone pseudo user. Disabled by default.' >> maimail.conf
            echo '# When enabled, ACL can be created, that apply to "All authenticated users"' >> maimail.conf
            echo '# This should probably only be activated on mail hosts, that are used exclusively by one organisation.' >> maimail.conf
            echo '# Otherwise a user might share data with too many other users.' >> maimail.conf
            echo 'ACL_ANYONE=disallow' >> maimail.conf
            ;;
        FTS_HEAP)
            echo '# Dovecot Indexing (FTS) Process maximum heap size in MB, there is no recommendation, please see Dovecot docs.' >> maimail.conf
            echo '# Flatcurve is used as FTS Engine. It is supposed to be pretty efficient in CPU and RAM consumption.' >> maimail.conf
            echo '# Please always monitor your Resource consumption!' >> maimail.conf
            echo "FTS_HEAP=128" >> maimail.conf
            ;;
        SKIP_FTS)
            echo '# Skip FTS (Fulltext Search) for Dovecot on low-memory, low-threaded systems or if you simply want to disable it.' >> maimail.conf
            echo "# Dovecot inside maimail use Flatcurve as FTS Backend." >> maimail.conf
            echo "SKIP_FTS=y" >> maimail.conf
            ;;
        FTS_PROCS)
            echo '# Controls how many processes the Dovecot indexing process can spawn at max.' >> maimail.conf
            echo '# Too many indexing processes can use a lot of CPU and Disk I/O' >> maimail.conf
            echo '# Please visit: https://doc.dovecot.org/configuration_manual/service_configuration/#indexer-worker for more informations' >> maimail.conf
            echo "FTS_PROCS=1" >> maimail.conf
            ;;
        ENABLE_SSL_SNI)
            echo '# Create seperate certificates for all domains - y/n' >> maimail.conf
            echo '# this will allow adding more than 100 domains, but some email clients will not be able to connect with alternative hostnames' >> maimail.conf
            echo '# see https://wiki.dovecot.org/SSL/SNIClientSupport' >> maimail.conf
            echo "ENABLE_SSL_SNI=n" >> maimail.conf
            ;;
        SKIP_SOGO)
            echo '# Skip SOGo: Will disable SOGo integration and therefore webmail, DAV protocols and ActiveSync support (experimental, unsupported, not fully implemented) - y/n' >> maimail.conf
            echo "SKIP_SOGO=n" >> maimail.conf
            ;;
        MAILDIR_SUB)
            echo '# MAILDIR_SUB defines a path in a users virtual home to keep the maildir in. Leave empty for updated setups.' >> maimail.conf
            echo "#MAILDIR_SUB=Maildir" >> maimail.conf
            echo "MAILDIR_SUB=" >> maimail.conf
            ;;
        WATCHDOG_NOTIFY_WEBHOOK)
            echo '# Send notifications to a webhook URL that receives a POST request with the content type "application/json".' >> maimail.conf
            echo '# You can use this to send notifications to services like Discord, Slack and others.' >> maimail.conf
            echo '#WATCHDOG_NOTIFY_WEBHOOK=https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' >> maimail.conf
            ;;
        WATCHDOG_NOTIFY_WEBHOOK_BODY)
            echo '# JSON body included in the webhook POST request. Needs to be in single quotes.' >> maimail.conf
            echo '# Following variables are available: SUBJECT, BODY' >> maimail.conf
            WEBHOOK_BODY='{"username": "maimail Watchdog", "content": "**${SUBJECT}**\n${BODY}"}'
            echo "#WATCHDOG_NOTIFY_WEBHOOK_BODY='${WEBHOOK_BODY}'" >> maimail.conf
            ;;
        WATCHDOG_NOTIFY_BAN)
            echo '# Notify about banned IP. Includes whois lookup.' >> maimail.conf
            echo "WATCHDOG_NOTIFY_BAN=y" >> maimail.conf
            ;;
        WATCHDOG_NOTIFY_START)
            echo '# Send a notification when the watchdog is started.' >> maimail.conf
            echo "WATCHDOG_NOTIFY_START=y" >> maimail.conf
            ;;
        WATCHDOG_SUBJECT)
            echo '# Subject for watchdog mails. Defaults to "Watchdog ALERT" followed by the error message.' >> maimail.conf
            echo "#WATCHDOG_SUBJECT=" >> maimail.conf
            ;;
        WATCHDOG_EXTERNAL_CHECKS)
            echo '# Checks if maimail is an open relay. Requires a SAL. More checks will follow.' >> maimail.conf
            echo '# No data is collected. Opt-in and anonymous.' >> maimail.conf
            echo '# Will only work with unmodified maimail setups.' >> maimail.conf
            echo "WATCHDOG_EXTERNAL_CHECKS=n" >> maimail.conf
            ;;
        SOGO_EXPIRE_SESSION)
            echo '# SOGo session timeout in minutes' >> maimail.conf
            echo "SOGO_EXPIRE_SESSION=480" >> maimail.conf
            ;;
        REDIS_PORT)
            echo "REDIS_PORT=127.0.0.1:7654" >> maimail.conf
            ;;
        DOVECOT_MASTER_USER)
            echo '# DOVECOT_MASTER_USER and _PASS must _both_ be provided. No special chars.' >> maimail.conf
            echo '# Empty by default to auto-generate master user and password on start.' >> maimail.conf
            echo '# User expands to DOVECOT_MASTER_USER@maimail.local' >> maimail.conf
            echo '# LEAVE EMPTY IF UNSURE' >> maimail.conf
            echo "DOVECOT_MASTER_USER=" >> maimail.conf
            ;;
        DOVECOT_MASTER_PASS)
            echo '# LEAVE EMPTY IF UNSURE' >> maimail.conf
            echo "DOVECOT_MASTER_PASS=" >> maimail.conf
            ;;
        MAILCOW_PASS_SCHEME)
            echo '# Password hash algorithm' >> maimail.conf
            echo '# Only certain password hash algorithm are supported. For a fully list of supported schemes,' >> maimail.conf
            echo '# see https://docs.maimail.email/models/model-passwd/' >> maimail.conf
            echo "MAILCOW_PASS_SCHEME=BLF-CRYPT" >> maimail.conf
            ;;
        ADDITIONAL_SERVER_NAMES)
            echo '# Additional server names for maimail UI' >> maimail.conf
            echo '#' >> maimail.conf
            echo '# Specify alternative addresses for the maimail UI to respond to' >> maimail.conf
            echo '# This is useful when you set mail.* as ADDITIONAL_SAN and want to make sure mail.maildomain.com will always point to the maimail UI.' >> maimail.conf
            echo '# If the server name does not match a known site, Nginx decides by best-guess and may redirect users to the wrong web root.' >> maimail.conf
            echo '# You can understand this as server_name directive in Nginx.' >> maimail.conf
            echo '# Comma separated list without spaces! Example: ADDITIONAL_SERVER_NAMES=a.b.c,d.e.f' >> maimail.conf
            echo 'ADDITIONAL_SERVER_NAMES=' >> maimail.conf
            ;;
        WEBAUTHN_ONLY_TRUSTED_VENDORS)
            echo "# WebAuthn device manufacturer verification" >> maimail.conf
            echo '# After setting WEBAUTHN_ONLY_TRUSTED_VENDORS=y only devices from trusted manufacturers are allowed' >> maimail.conf
            echo '# root certificates can be placed for validation under maimail-dockerized/data/web/inc/lib/WebAuthn/rootCertificates' >> maimail.conf
            echo 'WEBAUTHN_ONLY_TRUSTED_VENDORS=n' >> maimail.conf
            ;;
        SPAMHAUS_DQS_KEY)
            echo "# Spamhaus Data Query Service Key" >> maimail.conf
            echo '# Optional: Leave empty for none' >> maimail.conf
            echo '# Enter your key here if you are using a blocked ASN (OVH, AWS, Cloudflare e.g) for the unregistered Spamhaus Blocklist.' >> maimail.conf
            echo '# If empty, it will completely disable Spamhaus blocklists if it detects that you are running on a server using a blocked AS.' >> maimail.conf
            echo '# Otherwise it will work as usual.' >> maimail.conf
            echo 'SPAMHAUS_DQS_KEY=' >> maimail.conf
            ;;
        WATCHDOG_VERBOSE)
            echo '# Enable watchdog verbose logging' >> maimail.conf
            echo 'WATCHDOG_VERBOSE=n' >> maimail.conf
            ;;
        SKIP_UNBOUND_HEALTHCHECK)
            echo '# Skip Unbound (DNS Resolver) Healthchecks (NOT Recommended!) - y/n' >> maimail.conf
            echo 'SKIP_UNBOUND_HEALTHCHECK=n' >> maimail.conf
            ;;
        DISABLE_NETFILTER_ISOLATION_RULE)
            echo '# Prevent netfilter from setting an iptables/nftables rule to isolate the maimail docker network - y/n' >> maimail.conf
            echo '# CAUTION: Disabling this may expose container ports to other neighbors on the same subnet, even if the ports are bound to localhost' >> maimail.conf
            echo 'DISABLE_NETFILTER_ISOLATION_RULE=n' >> maimail.conf
            ;;
        HTTP_REDIRECT)
            echo '# Redirect HTTP connections to HTTPS - y/n' >> maimail.conf
            echo 'HTTP_REDIRECT=n' >> maimail.conf
            ;;
        ENABLE_IPV6)
            echo '# IPv6 Controller Section' >> maimail.conf
            echo '# This variable controls the usage of IPv6 within maimail.' >> maimail.conf
            echo '# Can either be true or false | Defaults to true' >> maimail.conf
            echo '# WARNING: MAKE SURE TO PROPERLY CONFIGURE IPv6 ON YOUR HOST FIRST BEFORE ENABLING THIS AS FAULTY CONFIGURATIONS CAN LEAD TO OPEN RELAYS!' >> maimail.conf
            echo '# A COMPLETE DOCKER STACK REBUILD (compose down && compose up -d) IS NEEDED TO APPLY THIS.' >> maimail.conf
            echo ENABLE_IPV6=${IPV6_BOOL} >> maimail.conf
            ;;
        SKIP_CLAMD)
            echo '# Skip ClamAV (clamd-maimail) anti-virus (Rspamd will auto-detect a missing ClamAV container) - y/n' >> maimail.conf
            echo 'SKIP_CLAMD=n' >> maimail.conf
            ;;
        SKIP_OLEFY)
            echo '# Skip Olefy (olefy-maimail) anti-virus for Office documents (Rspamd will auto-detect a missing Olefy container) - y/n' >> maimail.conf
            echo 'SKIP_OLEFY=n' >> maimail.conf
            ;;
        REDISPASS)
            echo "REDISPASS=$(LC_ALL=C </dev/urandom tr -dc A-Za-z0-9 2>/dev/null | head -c 28)" >> maimail.conf
            ;;
        SOGO_URL_ENCRYPTION_KEY)
            echo '# SOGo URL encryption key (exactly 16 characters, limited to A–Z, a–z, 0–9)' >> maimail.conf
            echo '# This key is used to encrypt email addresses within SOGo URLs' >> maimail.conf
            echo "SOGO_URL_ENCRYPTION_KEY=$(LC_ALL=C </dev/urandom tr -dc A-Za-z0-9 2>/dev/null | head -c 16)" >> maimail.conf
            ;;
        *)
            echo "${option}=" >> maimail.conf
            ;;
    esac
  done
}