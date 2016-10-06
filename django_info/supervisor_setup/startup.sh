#! /bin/bash 
 
NAME=supervisord
SUPERVISORD=/opt/www/myproj_venv/bin/supervisord
SUPERVISORCTL=/opt/www/myproj_venv/bin/supervisorctl
PIDFILE=/opt/www/myproj_var/supervisord/supervisord.pid
OPTS="-c /opt/www/myproj/myproj/code/config/supervisord/supervisord.conf"
PS=$NAME
TRUE=1
FALSE=0
 
 
isRunning(){
    pidof_daemon
    PID=$?
 
    if [ $PID -gt 0 ]; then
	return 1
    else
        return 0
    fi
}
 
pidof_daemon() {
    PIDS=`pidof -x $PS` || true
 
    [ -e $PIDFILE ] && PIDS2=`cat $PIDFILE`
 
    for i in $PIDS; do
        if [ "$i" = "$PIDS2" ]; then
            return 1
        fi
    done
    return 0
}
 
start () {
    echo "Starting Supervisor daemon manager..."
    isRunning
    isAlive=$?
 
    if [ "${isAlive}" -eq $TRUE ]; then
        echo "Supervisor is already running."
    else
        $SUPERVISORD $OPTS || echo "Failed...!"
        echo "OK"
    fi
}
 
stop () {
    echo "Stopping Supervisor daemon manager..."
    $SUPERVISORCTL $OPTS shutdown ||  echo "Failed...!"
    echo "OK"
}
 
case "$1" in
  start)
    start
	;;
 
  stop)
    stop
	;;
 
  restart|reload|force-reload)
    stop
    start
    ;;
  *)
    start
    ;;
 
esac
 
exit 0
