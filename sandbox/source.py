def foo():
    x = 1
    y = 2
    z = 3
    return x + y + z
try:
        repo = open_repository(path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return ExitCode.DATAERR
