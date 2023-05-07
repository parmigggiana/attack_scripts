from pwn import log

from milkman import local_test


@local_test
def exploit(target_ip):
    log.info(f"{__name__} against {target_ip}!")


def main():
    exploit()  # type: ignore


if __name__ == "__main__":
    main()
