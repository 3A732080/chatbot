import json
import requests
from datetime import datetime
from helper_fun import clean_json_string, dd, dump, load_file_content, save_content
import os, time

class GoogleGemini:
    def add_question_to_data(self, data, filepath, append_text = None):
        if append_text != None:
            text = load_file_content(filepath)

            data['contents'].append({
                "role": "user",
                "parts": [{"text":
                    rf"""
                    {text}
                    ---
                    {append_text}
                    """
                }]
            })
        else:
            data['contents'].append({
                "role": "user",
                "parts": [{"text": load_file_content(filepath)}]
            })

    def send_request_and_process_response(self, session, url, headers, data):
        status = 0

        while (status != 200):
            response = session.post(url, headers=headers, json=data)
            status = response.status_code

            time.sleep(1)

        response_content = response.json()['candidates'][0]['content']
        data['contents'].append(response_content)


    def get_answer_sql(self, filepath, index = 0):
        index_goal = -1

        try:
            data = json.loads(load_file_content(filepath))
            if len(data) == 46 and index == 0:
                 index_goal = 43
            if len(data) == 4 and index == 0:
                 index_goal = 1

            answer_text = json.loads(clean_json_string(data[index_goal]['parts'][0]['text'], True))

            return answer_text["sql"].replace("\\n", " ")
        except Exception as e:
            try:
                answer_text = json.loads(clean_json_string(data[index_goal]['parts'][0]['text'], True)[7:-3])

                return answer_text["sql"].replace("\\n", " ")
            except Exception as e:
                try:
                    answer_text = json.loads(clean_json_string(data[index_goal]['parts'][0]['text']))

                    return answer_text["sql"].replace("\\n", " ")
                except Exception as e:
                    return str(e)

    def check_error_answer(self, filepath):
        data = json.loads(load_file_content(filepath))
        return clean_json_string(data[0]['parts'][0]['text'])

    def main(self, index, continue_text = None, temperature = 1, top_p = 1):
        api_key = load_file_content('./google_gemini.env')
        api_key_bear = load_file_content('./google_gemini_bear.env')
        session = requests.Session()

        single_question = False
        url = f'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}'
        headers = {'Content-Type': 'application/json'}

        # fine-tuning
        single_question = True
        # url = f'https://generativelanguage.googleapis.com/v1beta/tunedModels/:generateContent'
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Authorization': f'Bearer {api_key_bear}'
        # }

        data = {
            "contents": [],
            "generationConfig": {
                "temperature": float(temperature),
                "topP": float(top_p),
            }
        }
 
        data['contents'] = []
        # data['contents'] = self.main_by_prepare(True, temperature, top_p)

        if continue_text == None:
            self.add_question_to_data(data, f"./input/test/{index}_question.txt")
        elif continue_text != None and single_question == True:
            self.add_question_to_data(data, f"./input/test/{index}_question.txt", continue_text)
        else:
            data['contents'] = json.loads(load_file_content(f"./output/google_gemini/{index}_{temperature}_{top_p}_question.json"))
            data['contents'].append({
                "role": "user",
                "parts": [{"text": continue_text}]
            })

        self.send_request_and_process_response(session, url, headers, data)

        save_content(data['contents'], f"./output/google_gemini/{index}_{temperature}_{top_p}_question.json")


    def main_by_prepare(self, finish = False, temperature = 1, top_p = 1):
        if finish == True:
            return json.loads(load_file_content(f"./input/prepare/google_gemini/prepare_{temperature}_{top_p}_result.json"))

        api_key = load_file_content('./google_gemini.env')
        session = requests.Session()

        url = f'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}'
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [],
            "generationConfig": {
                "temperature": float(temperature),
                "topP": float(top_p),
            }
        }

        # 資料集:LeetCode
        # lists = [1, 3, 4, 5, 6, 7, 9, 12, 14, 15, 16, 24, 26, 27, 28, 29, 30, 31, 36, 37, 38]

        # 資料集:CJDate
        lists = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

        for index in lists:
            time.sleep(15)

            if index != 1:
                data['contents'] = json.loads(load_file_content(f"./input/prepare/google_gemini/prepare_{temperature}_{top_p}_result.json"))

            # self.add_question_to_data(data, f"./input/prepare/cot_leetcode/{index}_cot.txt")
            # self.add_question_to_data(data, f"./input/prepare/cot_leetcode_Compared_Ours/{index}_cot.txt")
            # self.add_question_to_data(data, f"./input/prepare/cot_CJDate_Compared_Ours/{index}_cot.txt")
            self.add_question_to_data(data, f"./input/prepare/cot_CJDate_Ours/{index}_cot.txt")

            self.send_request_and_process_response(session, url, headers, data)

            save_content(data['contents'], f"./input/prepare/google_gemini/prepare_{temperature}_{top_p}_result.json")

        return json.loads(load_file_content(f"./input/prepare/google_gemini/prepare_{temperature}_{top_p}_result.json"))
