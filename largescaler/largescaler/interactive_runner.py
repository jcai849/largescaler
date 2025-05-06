import pexpect

class InteractiveRunner:
    '''\
    run-interactive --run=radian '1+1' - interact
    '''
    def __init__(self, run: str, *args: str):
        self.proc = pexpect.spawn(run)
        for cmd in args:
            self.proc.sendline(cmd)

    def interact(self):
        self.proc.interact(escape_character=None)

def main():
    import fire
    fire.Fire(InteractiveRunner)

if __name__ == "__main__":
    main()
