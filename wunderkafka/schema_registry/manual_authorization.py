import subprocess

def has_tickets() -> bool:
    try:
        result = subprocess.check_output(["klist"])
        if b"Ticket cache" in result:
            return True
    except subprocess.CalledProcessError:
        return False
    return False

def get_ticket(cmd: str) -> None:
    subprocess.run(cmd.split(), stdout=subprocess.PIPE, check=True)
    if has_tickets():
        return
    raise ValueError('Error creating kerberos ticket')

