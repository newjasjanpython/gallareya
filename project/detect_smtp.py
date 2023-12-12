import smtplib

def detect_smtp_port(email_host):
    default_ports = {
        'smtp': 25,  # Default SMTP port
        'smtps': 465,  # Default SMTP over SSL/TLS port
        'submission': 587  # Default port for message submission
    }
    try:
        _, _, host_protocol = email_host.partition(':')
        host, _, protocol = host_protocol.partition(':')
        port = smtplib.SMTP_PORT
        if protocol:
            port = default_ports.get(protocol, port)
        else:
            port = default_ports.get(host_protocol, port)
        return port
    except:
        return smtplib.SMTP_PORT
