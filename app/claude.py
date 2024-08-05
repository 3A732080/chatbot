import anthropic, json, time 
from datetime import datetime
from helper_fun import clean_json_string, dd, dump, load_file_content, save_content

class Claude:
    def add_message(self, messages, role, text):
        """添加對話到messages列表"""
        messages.append({
            "role": role,
            "content": [{"type": "text", "text": text}]
        })

    def get_answer_sql(self, filepath, index = 0):
        index_goal = -1

        try:
            data = json.loads(load_file_content(filepath))
            if len(data) == 46 and index == 0:
                 index_goal = 43
            if len(data) == 4 and index == 0:
                 index_goal = 1
            answer_text = json.loads(clean_json_string(data[index_goal]['content'][0]['text']))

            return answer_text["sql"].replace("\\n", " ")
        except Exception as e:
            try:
                answer_text = json.loads(clean_json_string(data[index_goal]['content'][0]['text'])[7:-3])

                return answer_text["sql"].replace("\\n", " ")
            except Exception as e:
                return str(e)

    def main(self, index, continue_text = None, temperature = 1, top_p = 1):
        api_key = load_file_content('./claude.env')

        client = anthropic.Anthropic(api_key=api_key)

        messages = []
        # messages = self.main_by_prepare(True, temperature, top_p)

        if continue_text == None:
            question_text = load_file_content(f"./input/test/{index}_question.txt")
            self.add_message(messages, "user", question_text)
        else:
            messages = json.loads(load_file_content(f"./output/claude/{index}_{temperature}_{top_p}_question.json"))
            self.add_message(messages, "user", continue_text)

        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=3000,
            temperature=float(temperature),
            top_p=float(top_p),
            messages=messages
        )

        response_text = message.content[0].text if message.content else ""

        self.add_message(messages, "assistant", response_text)
        save_content(messages, f"./output/claude/{index}_{temperature}_{top_p}_question.json")


    def main_by_prepare(self, finish = False, temperature = 1, top_p = 1):
        if finish == True:
            return json.loads(load_file_content(f"./input/prepare/claude/prepare_{temperature}_{top_p}_result.json"))

        api_key = load_file_content('./claude.env')

        client = anthropic.Anthropic(api_key=api_key)

        # 資料集:LeetCode
        # lists = [1, 3, 4, 5, 6, 7, 9, 12, 14, 15, 16, 24, 26, 27, 28, 29, 30, 31, 36, 37, 38]

        # 資料集:CJDate
        lists = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

        for index in lists:
            time.sleep(15)

            messages = []

            if index != 1:
                messages = json.loads(load_file_content(f"./input/prepare/claude/prepare_{temperature}_{top_p}_result.json"))

            # cot_text = load_file_content(f"./input/prepare/cot_leetcode_with_DE/{index}_cot.txt")
            # cot_text = load_file_content(f"./input/prepare/cot_leetcode_without_DE/{index}_cot.txt")
            # cot_text = load_file_content(f"./input/prepare/cot_CJDate_without_DE/{index}_cot.txt")
            cot_text = load_file_content(f"./input/prepare/cot_CJDate_with_DE/{index}_cot.txt")
            self.add_message(messages, "user", cot_text)

            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=float(temperature),
                top_p=float(top_p),
                messages=messages
            )

            response_text = message.content[0].text if message.content else ""

            self.add_message(messages, "assistant", response_text)
            save_content(messages, f"./input/prepare/claude/prepare_{temperature}_{top_p}_result.json")

        return json.loads(load_file_content(f"./input/prepare/claude/prepare_{temperature}_{top_p}_result.json"))