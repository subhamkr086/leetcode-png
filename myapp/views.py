from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
import requests
import json
import datetime
import pyperclip

def make_request(username):
    # Define the URL of the GraphQL endpoint
    url = 'https://leetcode.com/graphql'

    # Define the query or mutation
    query = """
        query userProfileUserQuestionProgressV2($userSlug: String!) {
            userProfileUserQuestionProgressV2(userSlug: $userSlug) {
                numAcceptedQuestions {
                    count
                    difficulty
                }
                numUntouchedQuestions {
                    count
                    difficulty
                }
            }
            matchedUser(username: $userSlug) {
                profile {
                    ranking
                    realName
                }
            }
        }
    """

    variables = {
        "userSlug": username
    }

    payload = {
        'query': query,
        'variables': variables
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        res = response.json()
        print(res)
        if 'errors' in res:
            return {}

        question_solved = [
            res['data']['userProfileUserQuestionProgressV2']['numAcceptedQuestions'][0]['count'],
            res['data']['userProfileUserQuestionProgressV2']['numAcceptedQuestions'][1]['count'],
            res['data']['userProfileUserQuestionProgressV2']['numAcceptedQuestions'][2]['count']
        ]
        total_questions = [
            res['data']['userProfileUserQuestionProgressV2']['numUntouchedQuestions'][0]['count'] + res['data']['userProfileUserQuestionProgressV2']['numAcceptedQuestions'][0]['count'],
            res['data']['userProfileUserQuestionProgressV2']['numUntouchedQuestions'][1]['count'] + res['data']['userProfileUserQuestionProgressV2']['numAcceptedQuestions'][1]['count'],
            res['data']['userProfileUserQuestionProgressV2']['numUntouchedQuestions'][2]['count'] + res['data']['userProfileUserQuestionProgressV2']['numAcceptedQuestions'][2]['count']
        ]
        name = res['data']['matchedUser']['profile']['realName']
    
        context = {
            'name': name if name !='' else 'No Name',
            'rank': res['data']['matchedUser']['profile']['ranking'],
            'question_solved' : question_solved,
            'total_questions' : total_questions,
            'no_of_questions_solved' : sum(question_solved),
            'total_no_of_questions' : sum(total_questions),
            'percent_of_questions_solved' : sum(question_solved) / sum(total_questions) * 100,
        }
        return context

    else:
        print(f"Query failed with status code {response.status_code}")
        print(response.text)
        return {}
    

def make_request_calender(username):
    # Define the URL of the GraphQL endpoint
    url = 'https://leetcode.com/graphql'

    # Define the query or mutation
    query = """
    query userProfileCalendar($username: String!, $year: Int) {
        matchedUser(username: $username) {
            userCalendar(year: $year) {
                submissionCalendar
            }
        }
    }
    """

    variables = {
        "username": username
    }

    payload = {
        'query': query,
        'variables': variables
    }

    response = requests.post(url, json=payload)
    dictionary = {}
    res = response.json()

    if response.status_code == 200:
        if 'errors' in res:
            return {}
    else:
        print(f"Query failed with status code {response.status_code}")
        print(response.text)
        return {}

    
    dictionary = json.loads(res['data']['matchedUser']['userCalendar']['submissionCalendar'])

    date_dict = {datetime.datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d'): value
             for timestamp, value in dictionary.items()}

    current_date = datetime.datetime.utcnow()
    year_before_date = current_date - datetime.timedelta(days=365)
    week_before = year_before_date.isocalendar()[1]

    date = year_before_date.date()
    string = """"""

    while date <= current_date.date():

        month_number = date.month
        year_number = date.year
        day_number_weekday = date.weekday()
        week_number = date.isocalendar()[1]

        x = (week_number - week_before + (month_number-current_date.month))*9 if current_date.year != year_number else (52-week_before+week_number + (12-current_date.month+month_number))*9
        color = "#D6D6D6"

        if str(date) in date_dict:
            # print(date)
            no_of_question = date_dict[str(date)]
            if no_of_question == 1: color = "#66d166"
            elif no_of_question == 2: color = "#65b465"
            elif no_of_question == 3: color = "#5ba35b"
            elif no_of_question <= 10: color = "#55a055"
            elif no_of_question > 10: color = "#427b42"
        
        temp = f"""<rect x="{2+x}" y="{250 + 9*day_number_weekday}" width="8" height="8" rx="2" ry="2" fill="{color}"></rect>\n"""
        string += temp
        date += datetime.timedelta(days=1)
    
    pyperclip.copy(string)
    return string

class return_html_response(View):
    def get(self, request, username=None):
        user = make_request(username=username)
        string = make_request_calender(username=username)

        if not user:
            svg_content = """
            <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="300" 
                height="300" 
                viewBox="0 0 512 512" 
                shape-rendering="geometricPrecision" 
                text-rendering="geometricPrecision" 
                image-rendering="optimizeQuality" 
                fill-rule="evenodd" 
                clip-rule="evenodd">
                <g fill-rule="nonzero">
                    <path fill="#D92D27" d="M492.56 431.15H19.42v-.05c-14.72.03-24.33-16.08-16.78-29.12L234.51 9.64c7.35-12.57 25.75-13.05 33.42-.23l240.41 390.96c9.12 12.64.2 30.78-15.78 30.78"/>
                    <path fill="#fff" d="M41.15 399.63h431.88L252.71 47.08c-.63-.99-1.38-.98-1.97 0L40.02 397.9c-.63 1.12-.31 1.74 1.13 1.73"/>
                    <path d="M243.18 246.58h25.46v20.32h-25.46zm-78.9 102.8h-17.43v7.87h21.35v12.7h-38.78v-54.47h38.35l-2.18 12.69h-18.74v8.58h17.43zm58.16 20.57h-19.16l-7.15-16.21h-5v16.21h-16.18v-54.47h27.45c12.49 0 18.74 6.36 18.74 19.08 0 8.72-2.7 14.47-8.11 17.26zm-31.31-41.78v12.15h5.26c2.09 0 3.62-.23 4.57-.66s1.44-1.44 1.44-3v-4.82c0-1.57-.49-2.58-1.44-3.01s-2.49-.66-4.57-.66zm84.25 41.78h-19.17l-7.15-16.21h-4.99v16.21h-16.18v-54.47h27.45c12.49 0 18.74 6.36 18.74 19.08 0 8.72-2.7 14.47-8.11 17.26zm-31.31-41.78v12.15h5.25c2.1 0 3.63-.23 4.58-.66s1.44-1.44 1.44-3v-4.82c0-1.57-.49-2.58-1.44-3.01s-2.5-.66-4.58-.66zm34.14 14.59c0-9.94 1.86-17.18 5.58-21.74 3.71-4.57 10.43-6.85 20.13-6.85s16.41 2.28 20.13 6.85c3.72 4.56 5.58 11.8 5.58 21.74 0 4.94-.4 9.09-1.18 12.46s-2.14 6.3-4.05 8.8c-1.92 2.5-4.57 4.33-7.93 5.49-3.37 1.16-7.55 1.74-12.55 1.74-4.99 0-9.18-.58-12.55-1.74s-6.01-2.99-7.93-5.49-3.27-5.43-4.05-8.8c-.79-3.37-1.18-7.52-1.18-12.46m18.74-9.07v22.66h7.23c2.38 0 4.11-.27 5.19-.83 1.07-.55 1.61-1.81 1.61-3.79v-22.66h-7.33c-2.32 0-4.02.28-5.09.83s-1.61 1.81-1.61 3.79m85.62 36.26H363.4l-7.15-16.21h-4.99v16.21h-16.18v-54.47h27.44q18.75 0 18.75 19.08c0 8.72-2.71 14.47-8.11 17.26zm-31.31-41.78v12.15h5.25c2.1 0 3.63-.23 4.58-.66s1.43-1.44 1.43-3v-4.82c0-1.57-.48-2.58-1.43-3.01s-2.5-.66-4.58-.66zm-82.62-93h-25.46c-1.82-22.29-4.73-26.26-5.95-40.78-1.25-14.61-2.12-35.58 18.73-35.58 21.86 0 20.1 23.36 18.45 38.47-1.37 12.45-4.05 17.16-5.77 37.89"/>
                </g>
            </svg>
            """
            return HttpResponse(svg_content, content_type="image/svg+xml")
        svg_content = f"""
                <svg width="600" height="700" xmlns="http://www.w3.org/2000/svg" viewbox="0 0 600 800">
                <image 
                    href="https://cdn.iconscout.com/icon/free/png-256/free-leetcode-3628885-3030025.png?f=webp" 
                    x="20" 
                    y="15" 
                    width="50" 
                    height="50"/>
                <text 
                    x="80" 
                    y="45" 
                    font-family="Arial" 
                    font-size="23">{user['name']}</text>
                <text 
                    x="580" 
                    y="45" 
                    font-family="Arial" 
                    font-size="20" 
                    fill="#817e78" 
                    text-anchor="end">#{user['rank']}</text>
                
                <circle
                    cx="90" 
                    cy="150" 
                    r="70" 
                    fill="none" 
                    stroke="#ddd" 
                    stroke-width="10" 
                />
                <circle
                    cx="90"
                    cy="150"
                    r="70"
                    fill="none"
                    stroke="#e18000"
                    stroke-width="10"
                    stroke-dasharray="439.6"
                    stroke-dashoffset="calc(439.6 - (439.6 * var(--percent)) / 100)"
                    style="--percent: {user['percent_of_questions_solved']};" 
                />
                
                <text 
                    x="92" 
                    y="156"
                    font-size="20" 
                    text-anchor="middle">
                    {user['no_of_questions_solved']}/{user['total_no_of_questions']}
                </text>

                <text 
                    x="200" 
                    y="85"
                    fill="#000" 
                    font-size="16" 
                >
                    Easy
                    <tspan x="96.5%" text-anchor="end">{(user['question_solved'][0])}/{user['total_questions'][0]}</tspan>
                </text>
                <rect 
                    x="200" 
                    y="90" 
                    width="380" 
                    height="10" 
                    fill="#ddd" 
                    rx="5" 
                    ry="5" 
                />
                
                <!-- Progress rectangle -->
                <rect 
                    x="200" 
                    y="90" 
                    width="calc(380 * {user['question_solved'][0]/user['total_questions'][0]})" 
                    height="10" 
                    fill="#1e8600" 
                    rx="5" 
                    ry="5" 
                />

                <text 
                    x="200" 
                    y="145"
                    fill="#000" 
                    font-size="16" 
                >
                    Medium
                    <tspan x="96.5%" text-anchor="end">{(user['question_solved'][1])}/{user['total_questions'][1]}</tspan>
                </text>
                <rect 
                    x="200" 
                    y="150" 
                    width="380" 
                    height="10" 
                    fill="#ddd" 
                    rx="5" 
                    ry="5" 
                />
                
                <!-- Progress rectangle -->
                <rect 
                    x="200" 
                    y="150" 
                    width="calc(380 * {user['question_solved'][1]/user['total_questions'][1]})" 
                    height="10" 
                    fill="#ff7300" 
                    rx="5" 
                    ry="5" 
                />

                <text 
                    x="200" 
                    y="205"
                    fill="#000" 
                    font-size="16" 
                >
                    Hard
                    <tspan x="96.5%" text-anchor="end">{(user['question_solved'][2])}/{user['total_questions'][2]}</tspan>
                </text>
                <rect 
                    x="200" 
                    y="210" 
                    width="380" 
                    height="10" 
                    fill="#ddd" 
                    rx="5" 
                    ry="5" 
                />
                
                <!-- Progress rectangle -->
                <rect 
                    x="200" 
                    y="210" 
                    width="calc(380 * {user['question_solved'][2]/user['total_questions'][2]})" 
                    height="10" 
                    fill="#be0404" 
                    rx="5" 
                    ry="5" 
                />
                {string}
                </svg>
                """
        return HttpResponse(svg_content, content_type="image/svg+xml")