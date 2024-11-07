def parse_error_file(file_path):
    error_dict = {}

    with open(file_path, "r") as file:
        lines = file.readlines()

    for i in range(0, len(lines), 2):
        error_message = lines[i].strip()
        error_code_hex = lines[i + 1].strip()

        # Convert the hexadecimal error code to decimal
        try:
            error_code = int(error_code_hex, 16)
        except ValueError:
            error_code = error_code_hex

        error_dict[error_code] = error_message

    return error_dict


file_path = "errors.txt"

error_dict = parse_error_file(file_path)

print(error_dict)
