from sys import argv
from this import s
from numscript import io
from numscript import parser
from numscript.vm import VM


def main() -> None:
    if len(argv) == 1:
        print("Usage: numscript <script>")
        exit(1)
    
    script_string = io.load_file(argv[1])
    script = parser.parse(script_string)
    
    vm = VM()
    status = vm.run(script)

    print(f"Program finished with status code {status}")


if __name__ == '__main__':
    main()
