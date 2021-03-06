import csv
import re
import requests
import sys
from bs4 import BeautifulSoup

LOGIN_URL = "https://open.kattis.com/login/email"
BASEURL = "https://open.kattis.com"
URL = "https://open.kattis.com/problems?show_solved=on&show_tried=off&show_untried=off"


def main():
    if len(sys.argv) == 3:
        EMAIL = sys.argv[1]
        PASSWORD = sys.argv[2]
    else:
        EMAIL = input("Email Address: ")
        PASSWORD = input("Password: ")

    session_requests = requests.session()
    # Get csrf token
    result = session_requests.get(LOGIN_URL)
    soup = BeautifulSoup(result.content, "lxml")
    authenticity_token = soup.find(attrs={"name": "csrf_token"}).attrs['value']
    # Create payload
    payload = {
        "user": EMAIL,
        "password": PASSWORD,
        "csrf_token": authenticity_token
    }
    # Perform login
    result = session_requests.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))
    # Go to solved problems list
    result = session_requests.get(URL)
    soup = BeautifulSoup(result.content, 'lxml')
    # profile link is /users/$username
    profile = soup.find(href=re.compile("/users/.+")).attrs['href']

    # Save all listed problems
    problem_links = []
    problem_names = []
    problem_difficulties = []

    while True:
        for row in soup.find_all(class_=re.compile('(odd|even) solved$')):
            columns = row.contents
            name_fld = columns[1].find('a')
            problem_links.append(name_fld.attrs['href'])
            problem_names.append(name_fld.text)
            problem_difficulties.append(columns[17].text)
        next_btn = soup.find(id='problem_list_next')
        if next_btn.attrs['class'][0] == 'enabled':
            soup = BeautifulSoup(session_requests.get(BASEURL + next_btn.attrs['href']).content, 'lxml')
            continue
        break

    submission_date = []
    submission_lang = []
    submission_code = []

    for link in problem_links:
        problem = BASEURL + profile + "/submissions" + link[9:]
        result = session_requests.get(problem)
        soup = BeautifulSoup(result.content, 'lxml')
        tbl_body = soup.find("tbody")

        for row in tbl_body.find_all('tr'):
            # latest accepted solution
            accepted_row = row.find(class_='accepted')
            if accepted_row:
                if '-' in accepted_row.parent.parent.find(attrs={"data-type": "time"}).string:
                    submission_date.append(accepted_row.parent.parent.find(attrs={"data-type": "time"}).string)
                else:
                    from datetime import date
                    submission_date.append(date.today())
                submission_lang.append(accepted_row.parent.parent.find(attrs={"data-type": "lang"}).string)
                submission_page = BASEURL + accepted_row.parent.parent.find(class_="submission_id").a.attrs["href"]
                result = session_requests.get(submission_page)
                soup = BeautifulSoup(result.content, 'lxml')
                submission_code.append(soup.find(class_="source-highlight").text)
                break

    with open("Kattis.csv", "w", newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for i in range(0, len(problem_names)):
            writer.writerow(
                [problem_names[i], problem_links[i], problem_difficulties[i], submission_date[i], submission_lang[i],
                 submission_code[i]])

    print("Done! Check the Kattis.csv")


if __name__ == "__main__":
    main()
