import pandas as pd
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_form(str2print: str, how='b') -> str:
    if how=='b':
        return f"{bcolors.BOLD}{str2print}{bcolors.ENDC}"


def return_output(what: list, where: str, f_id: int, ab_groups: dict, fun_name: str):
    # create a DataFrame for convenience
    df = pd.DataFrame(what)

    if where == "terminal" or where == "both":
        print("-----------------------------------------------------")
        print(f"Results for the funnel {print_form(f_id)} -- {print_form(fun_name)}")
        if 'Control2' in ab_groups.keys():
            print(f"Control group is: {print_form(ab_groups['Control'])}, "
                  f"second Control group is: {print_form(ab_groups['Control2'])},"
                  f" test group is {print_form(ab_groups['Test'])}")
        else:
            print(f"Control group is: {print_form(ab_groups['Control'])}, "
                  f"test group is {print_form(ab_groups['Test'])}")
        print(df)
    if where == "csv" or where == "both":
        filename = f'{f_id}-{fun_name}.csv'
        print(f"results will be saved on the file {filename}")
        df.to_csv(filename)
