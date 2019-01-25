import pandas as pd
from tqdm import tqdm
from tabulate import tabulate


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_form(str2print, how='b') -> str:
    if how == 'b':
        return f"{Bcolors.BOLD}{str2print}{Bcolors.ENDC}"


def return_long_output(what: list, where: str, f_id: int, ab_groups: dict, fun_name: str):
    # create a DataFrame for convenience
    df = pd.DataFrame(what)

    if where == "terminal" or where == "both":
        tqdm.write("-----------------------------------------------------")
        tqdm.write(f"Results for the funnel {print_form(f_id)} -- {print_form(fun_name)}")
        if 'Control2' in ab_groups.keys():
            tqdm.write(f"Control group is: {print_form(ab_groups['Control'])}, "
                       f"second Control group is: {print_form(ab_groups['Control2'])},"
                       f" test group is {print_form(ab_groups['Test'])}")
        else:
            tqdm.write(f"Control group is: {print_form(ab_groups['Control'])}, "
                       f"test group is {print_form(ab_groups['Test'])}")
        tqdm.write("\n")
        tqdm.write(tabulate(df, headers="keys", showindex=False))
    if where == "csv" or where == "both":
        filename = f'{f_id}-{fun_name}.csv'
        tqdm.write(f"results will be saved on the file {filename}")
        df.to_csv(filename)


def create_group(row):
    if row['Discriminant'] == 'None':
        return 'All.' + row['Cohort']
    else:
        if '+' in row['Discriminant']:
            tmp = [a.split(".")[1] + "." + b for a, b in zip(row['Discriminant'].split('+'), row['Cohort'].split("+"))]
            toret = ""
            for i, val in enumerate(tmp):
                if i > 0:
                    toret += '+'
                toret += val
            return toret

        return row['Discriminant'].split('.')[1] + "." + row['Cohort']


def return_short_output(what, where, f_id, ab_groups, fun_name):
    # create a DataFrame for convenience
    df = pd.DataFrame(what)
    df['Group'] = df.apply(lambda row: create_group(row), axis=1)

    df.drop(columns=['Comment', 'Discriminant', 'Cohort'], inplace=True)
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df[cols]

    if where == "terminal" or where == "both":
        tqdm.write("-----------------------------------------------------")
        tqdm.write(f"Results for the funnel {print_form(f_id)} -- {print_form(fun_name)}")
        if 'Control2' in ab_groups.keys():
            tqdm.write(f"Control group is: {print_form(ab_groups['Control'])}, "
                       f"second Control group is: {print_form(ab_groups['Control2'])},"
                       f" test group is {print_form(ab_groups['Test'])}")
        else:
            tqdm.write(f"Control group is: {print_form(ab_groups['Control'])}, "
                       f"test group is {print_form(ab_groups['Test'])}")
        tqdm.write(tabulate(df, headers="keys", showindex=False))
    if where == "csv" or where == "both":
        filename = f'{f_id}-{fun_name}.csv'
        tqdm.write(f"results will be saved on the file {filename}")
        df.to_csv(filename)
    pass


def return_output(what: list, where: str, how: str, f_id: int, ab_groups: dict, fun_name: str):
    if how == 'long':
        return_long_output(what=what, where=where, f_id=f_id, ab_groups=ab_groups, fun_name=fun_name)
    elif how == 'short':
        return_short_output(what=what, where=where, f_id=f_id, ab_groups=ab_groups, fun_name=fun_name)
