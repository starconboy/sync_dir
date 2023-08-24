import argparse
import comparison
import shutil
import os


def print_diff_files(dcmp):
    for name in dcmp.diff_files:
        print("diff_file %s found in %s and %s" % (name, dcmp.left, dcmp.right))

    for sub_dcmp in dcmp.subdirs.values():
        print_diff_files(sub_dcmp)


def sync():
    # TODO: add docstring
    parser = argparse.ArgumentParser(description='Compares two directories for differences and syncronizes them')
    parser.add_argument('-s', '--source', required=True, help='Full path of the source directory')
    parser.add_argument('-d', '--destination', required=True, help='Full path of the destination directory')
    parser.add_argument('-r', '--recursive', required=False, default=True, action='store_true')
    parser.add_argument('-v', '--verbose', required=False, action='store_true')
    parser.add_argument('-f', '--force', required=False, action='store_true')
    args = parser.parse_args()
    print(args)

    # Compare source/destination
    compare = comparison.directory_compare()
    compare.search_differences(args.source, args.destination, args.recursive)
    compare.report()
    
    # Check destination drive space
    disk_stat = shutil.disk_usage(args.destination)
    space_requirement = compare.get_ending_diskspace_requirement()

    
    print(disk_stat)
    if disk_stat.free <= space_requirement:
        # There isn't enough diskspace for this sync job
        print("ERROR: not enough disk space for the syncronization job.  Please clear some disk space and try again.")
        print(space_requirement + " bytes of space needed as part of the job.")
        exit(1)
    
    print("This job will move result in a change of " + str(space_requirement) + " bytes.  Do you wish to continue? ")
    response = input("(Y or N): ")
    if response == "Y":
        compare.syncronize_directories()
        # continue to make the changes required...
    #     print("copy started....")
    #     for item in compare.differences:
    #         if item.is_dir:
    #             if item.add:
    #                 print("creating directory " + item.destination)
    #                 os.mkdir(item.destination)
    #             else:
    #                 print("delete directory, not implmented")
    #         else:
    #             if item.add:
    #                 print("coping " + item.source)
    #                 shutil.copy2(item.source, item.destination)
    #                 print("copy " + item.source + " complete")
    #             else:
    #                 print("deleting " + item.destination)
    #                 os.remove(item.destination)
    #                 print("deleted")


    
    # print("ending sync job")


    # Output differences - letting the user know if there is enough space or not.


if __name__ == '__main__':
    sync()