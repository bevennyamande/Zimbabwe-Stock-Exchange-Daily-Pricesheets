import os
from datetime import date
import pandas as pd
import git
from git import Git

URL = "https://www.zse.co.zw/price-sheet/"

git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
# git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

def get_todays_pricesheet(URL: str):
    """ Get the price sheet from the website """

    dataframe = pd.read_html(URL)
    return dataframe


def get_todays_date() -> str:
    """ Get todays date """

    today_date = date.today()
    return today_date.strftime("%d-%m-%Y") # dd-mm-YY


def set_todays_filename() ->str:
    """ Name to save the excel file """

    return f'{get_todays_date()}.xlsx'


def is_file_exist():
    """ Check if the file already exists """
    pass

def update_repo():
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        repo = git.Repo(".")
        repo.git.add("--all")
        repo.git.commit("-m files")
        repo.git.push()
    return



def main():
    df = get_todays_pricesheet(URL)
    df[0].to_excel(set_todays_filename(), header=True, index=False)
    # update_repo()

if __name__ == "__main__":
    main()
