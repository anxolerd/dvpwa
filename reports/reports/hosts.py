import idna


def to_ascii_hostname(hostname):
    return idna.encode(hostname).decode('ascii')


def is_valid_label(label):
    try:
        idna.check_label(label)
    except idna.IDNAError:
        return False
    return True
