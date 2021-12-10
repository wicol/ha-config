#!/usr/bin/env python3
import argparse
import sys
import socket
import logging

log = logging.getLogger("ps5.py")

DDP_VERSION = "00030010"
DDP_CLIENT_TYPE = "vr"
DDP_AUTH_TYPE = "R"
# This can differ.. in my case it was "a"
#DDP_MODEL = "m"
DDP_MODEL = "a"
DDP_APP_TYPE = "r"
PORT = 9302


def request_state(host):
    """
    Send a special HTTP like request over UDP(!)
    Response should be something like "HTTP/1.1 620 Server Standby" or
    "HTTP/1.1 200 Ok"
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    msg = (
    "SRCH * HTTP/1.1\n"
    f"device-discovery-protocol-version:{DDP_VERSION}"
    )
    try:
        log.debug("Sending:\n%s", msg)
        s.sendto(bytes(msg, "utf-8"), (host, PORT))
    except socket.error as e:
        log.error(e)
        return

    try:
        res_msg = s.recv(1024)
    except socket.timeout:
        log.info("Timeout waiting for response from ps5")
        # Probably in transition between standby and on or vice versa
        res_msg = ""
    s.close()
    return str(res_msg)


def wake(host, user_credential):
    """
    Send another special HTTP like request over UDP
    This one doesn't send a response so just return after the socket write
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    msg = (
    "WAKEUP * HTTP/1.1\n"
        f"client-type:{DDP_CLIENT_TYPE}\n"
        f"auth-type:{DDP_AUTH_TYPE}\n"
        f"model:{DDP_MODEL}\n"
        f"app-type:{DDP_APP_TYPE}\n"
        f"user-credential:{user_credential}\n"
        f"device-discovery-protocol-version:{DDP_VERSION}\n"
    )
    try:
        log.debug("Sending:\n%s", msg)
        s.sendto(bytes(msg, "utf-8"), (host, PORT))
    except socket.error as e:
        log.error(e)
        return
    finally:
        s.close()

    
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Wake or query a PS5 for state.")
    p.add_argument("host")
    p.add_argument("-d", "--debug", action="store_true", help="Log some more")
    p.add_argument("-b", "--binary-mode", action="store_true", help="Report standby as OFF")
    p.add_argument("-u", metavar="USER_CREDENTIALS", dest="credentials", help="User credentials for wake action")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("-q", "--query", action="store_true", help="Query PS5 for current state. Prints ON/STANDBY/OFF (Unreachable host = OFF)"),
    group.add_argument("-w", "--wake", action="store_true", help="Wake PS5 using user credentials. Exits immediately.")

    args = p.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.wake:
        if not args.credentials:
            print("Please supply user credentials with -u when performing a wake.")
            exit(1)
        response = wake(args.host, args.credentials)
        exit(0)
    elif args.query:
        response = request_state(args.host) or ""
        if "200 Ok" in response:
            state = "ON"
        elif not args.binary_mode and "620 Server Standby" in response:
            state = "STANDBY"
        else:
            state = "OFF"
        print(state)
