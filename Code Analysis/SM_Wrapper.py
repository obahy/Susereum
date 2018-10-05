import csv, time, os, subprocess, sys

working_dir = "D:/Users/AdEeL/Desktop/Practicum/Code Analysis/SourceMeter-8.2.0-x64-windows/Python/Demo/"
project_path = "ceilometer"
report_path = "Results"
project_name = "Test"
reports_dir = ""

def analyze_project():
    # SourceMeterPython –projectBaseDir=Project -resultsDir=Report -projectName=Test
    command_to_execute = "SourceMeterPython -projectBaseDir=" + project_path + " -resultsDir=" + report_path + " -projectName=" + project_name
    # number of files
    #print(working_dir+project_path)
    file_count = sum([len(files) for r, d, files in os.walk(working_dir+project_path)])
    reports_dir = time.strftime("%Y-%m-%d_%H-%M-%S").strip()
    print("\nStarting Code Analysis...", time.strftime("[ Time: %H:%M:%S, Files found:"), file_count, "Reports dir:", reports_dir, "]")
    # print("Working directory=", working_dir)
    print("Executing command:", command_to_execute, "\n")

    p = subprocess.Popen(command_to_execute, shell=True, stderr=subprocess.PIPE, cwd=working_dir)

    while True:
        out = "".join(p.stderr.read(1))  # reading and converting to string
        if out == '' and p.poll() != None:
            print("\nJob complete. Reports generated!")
            # return path
            return working_dir + report_path + "/" + project_name + "/" + "python" + "/" + reports_dir + "/"
            break

        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()


def read_write_file(data, cols, file_mode):
    data_rows, data_columns = len(data), len(data[0])

    with open('CodeAnalysis.csv', file_mode, newline='') as csv_out_file:
        out_writer = csv.writer(csv_out_file)
        if (file_mode == 'w'):  # write the header data in case of new file only.
            out_writer.writerow(["Hello Abel, this is your project ID"])  # Header on file
            out_writer.writerow(["Ref", "Ref-Name", "LOC", "CD", "Params"])  # Header on file
        for i in range(1, data_columns):
            if (file_mode == 'w'):
                out_writer.writerow(["Class", data[i][cols[0]], data[i][cols[1]], data[i][cols[2]], "0"])
                print("%-10s" % "Class", "%-30s" % data[i][cols[0]], "%-10s" % data[i][cols[1]],
                      "%-10s" % data[i][cols[2]], "%-10s" % "0")
            else:
                out_writer.writerow(["Method", data[i][cols[0]], data[i][cols[1]], data[i][cols[2]], data[i][cols[3]]])
                print("%-10s" % "Method", "%-30s" % data[i][cols[0]], "%-10s" % data[i][cols[1]],
                      "%-10s" % data[i][cols[2]], "%-10s" % data[i][cols[3]])


start_time = time.time()
# Run SourceMeter to generate reports...
csv_in_path = analyze_project()
print(csv_in_path)
# Fetch data from generated reports and create new file...
csv_class_file = project_name+"-Class.csv"
data = list(csv.reader(open(csv_in_path + csv_class_file)))
# 1 name, 38 LOC, 27 CD(Code Density), 39 NA(Number of Attribs)
csv_read_cols = [1, 38, 27, 39]  # sequence of column numbers that you want to write in the out file
print("\nFetching data from reports...\n")
print("%-10s" % "Ref", "%-30s" % "Ref-Name", "%-10s" % "LOC", "%-10s" % "CD", "%-10s" % "Params")  # Print once
print("----------------------------------------------------------------------")
read_write_file(data, csv_read_cols, 'w')

csv_method_file = project_name+"-Method.csv"
data = list(csv.reader(open(csv_in_path + csv_method_file)))
# 1 name, 30 LOC, 24 CD, 32 NUMPAR(number of parameters
csv_read_cols = [1, 30, 24, 32]  # sequence of column numbers that you want to write in the out file
read_write_file(data, csv_read_cols, 'a')

print("\nFile: CodeAnalysis.csv created!", time.strftime("[ Time: %H:%M:%S ]"))
elapsed_time = time.time() - start_time
print(time.strftime("Execution time: %H:%M:%S", time.gmtime(elapsed_time)))
