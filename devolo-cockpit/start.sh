#!/bin/bash
# (c) 2022 Michael Gebetsroither <m.gebetsr@gmail.com>

echo '# start daemon'
(
    cd /var/lib/devolonetsvc/ && nohup /usr/bin/devolonetsvc &
)

echo '# start devolo-cockpit'
exec /opt/devolo/dlancockpit/bin/dlancockpit-run.sh
