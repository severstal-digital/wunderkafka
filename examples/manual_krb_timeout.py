from wunderkafka.hotfixes.watchdog import KrbWatchDog

if __name__ == '__main__':
    krb = KrbWatchDog()
    krb.krb_timeout = 10  # complete
    krb.krb_timeout = 'something'  # raised TypeError
