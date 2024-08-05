import requests
import json
from datetime import datetime
import time
from helper_fun import clean_json_string, dd, dump, load_file_content, save_content

class ChatGpt:
    def call_chat_gpt_api(self, api_key, message, temperature = 1, top_p = 1):
        """使用 ChatGPT API 發送單個消息並獲得回應"""
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                },
                json={
                    # 'model': 'gpt-3.5-turbo',
                    'model': 'ft:gpt-3.5-turbo-1106:personal:cjdate-ours-v2:9RgJqpiw',
                    'messages': message,
                    'temperature': float(temperature),
                    'top_p': float(top_p),
                })
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            dd(f"[ChatGpt] API error: {e}")

    def get_answer_sql(self, filepath, index = 0):
        index_goal = -1

        try:
            data = json.loads(load_file_content(filepath))
            if len(data) == 46 and index == 0:
                 index_goal = 43
            if len(data) == 4 and index == 0:
                 index_goal = 1

            answer_text = json.loads(clean_json_string(data[index_goal]['content']))

            return answer_text["sql"].replace("\\n", " ")
        except Exception as e:
            try:
                answer_text = json.loads(clean_json_string(data[index_goal]['content'])[7:-3])

                return answer_text["sql"].replace("\\n", " ")
            except Exception as e:
                return str(e)

    def main(self, index, continue_text = None, temperature = 1, top_p = 1):
        api_key = load_file_content('./chat_gpt.env')

        messages = []
        # messages = self.main_by_prepare(True, temperature, top_p)

        if continue_text == None:
            question_text = load_file_content(f"./input/test/{index}_question.txt")
            messages.append({"role": "user", "content": question_text})
        else:
            messages = json.loads(load_file_content(f"./output/chat_gpt/{index}_{temperature}_{top_p}_question.json"))

            question_text = continue_text

            messages.append({
                "role": "user",
                 "content": question_text
            })

        content = self.call_chat_gpt_api(api_key, messages, temperature, top_p)

        if content and 'choices' in content and content['choices']:
            response_text = content['choices'][0].get('message', {}).get('content', '')

            messages.append({"role": "assistant", "content": response_text})

        save_content(messages, f"./output/chat_gpt/{index}_{temperature}_{top_p}_question.json")

    def main_by_prepare(self, finish = False, temperature = 1, top_p = 1):
        if finish == True:
            return json.loads(load_file_content(f"./input/prepare/chat_gpt/prepare_{temperature}_{top_p}_result.json"))

        api_key = load_file_content('./chat_gpt.env')

        # 資料集:LeetCode
        # lists = [1, 3, 4, 5, 6, 7, 9, 12, 14, 15, 16, 24, 26, 27, 28, 29, 30, 31, 36, 37, 38]

        # 資料集:CJDate
        lists = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

        for index in lists:
            time.sleep(15)
            messages = []

            if index != 1:
                messages = json.loads(load_file_content(f"./input/prepare/chat_gpt/prepare_{temperature}_{top_p}_result.json"))

            # cot_text = load_file_content(f"./input/prepare/cot_leetcode_with_DE/{index}_cot.txt")
            # cot_text = load_file_content(f"./input/prepare/cot_leetcode_without_DE/{index}_cot.txt")
            # cot_text = load_file_content(f"./input/prepare/cot_CJDate_without_DE/{index}_cot.txt")
            cot_text = load_file_content(f"./input/prepare/cot_CJDate_with_DE/{index}_cot.txt")

            messages.append({
                "role": "user",
                "content": cot_text
            })

            content = self.call_chat_gpt_api(api_key, messages, temperature, top_p)

            if content and 'choices' in content and content['choices']:
                response_text = content['choices'][0].get('message', {}).get('content', '')

                messages.append({"role": "assistant", "content": response_text})

                save_content(messages, f"./input/prepare/chat_gpt/prepare_{temperature}_{top_p}_result.json")

        return json.loads(load_file_content(f"./input/prepare/chat_gpt/prepare_{temperature}_{top_p}_result.json"))