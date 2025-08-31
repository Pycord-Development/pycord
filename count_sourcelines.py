# prints recursive count of lines of python source code from current directory
# includes an ignore_list. also prints total sloc

import os
cur_path = os.getcwd()
ignore_set = set(["__init__.py", "count_sourcelines.py"])

loc_list = []

for py_dir, _, py_files in os.walk(cur_path):
    for py_file in py_files:
        if py_file.endswith(".py") and py_file not in ignore_set:
            total_path = os.path.join(py_dir, py_file)
            try:
                # Open the file with UTF-8 encoding
                with open(total_path, "r", encoding="utf-8") as file:
                    loc_list.append((len(file.read().splitlines()),
                                     total_path.split(cur_path)[1]))
            except UnicodeDecodeError as e:
                print(f"Skipping file {total_path} due to encoding error: {e}")

for line_number_count, filename in loc_list:
    print("%05d lines in %s" % (line_number_count, filename))

print("\nTotal: %s lines (%s)" % (sum([x[0] for x in loc_list]), cur_path))
