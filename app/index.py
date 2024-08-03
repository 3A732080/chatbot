from pymssql_fun import DatabaseConnection
from google_gemini import GoogleGemini
from chat_gpt import ChatGpt
from claude import Claude
from db_sim_fun import compare_sql_structure, compare_results, calculate
from helper_fun import clean_json_string, dd, dump, load_file_content, error_format_text, is_string
import time
import sys

lists = [1, 2, 3, 4, 5, 6, 7, 8, 9]

def analyze_and_compare(lists):
    analyzers = {
        'chat_gpt': ChatGpt(),
        'google_gemini': GoogleGemini(),
        'claude': Claude(),
    }

    if len(sys.argv) > 2:
        for index, arg in enumerate(sys.argv[1:], 1):
            if index == 1:
                temperature = arg
                dump(f"temperature: {arg}")

            if index == 2:
                top_p = arg
                dump(f"top_p: {arg}")
    else:
        dd("請帶入 temperature、top_p 參數")

    # analyzers['google_gemini'].main_by_prepare(False, temperature, top_p)
    # analyzers['chat_gpt'].main_by_prepare(False, temperature, top_p)
    # analyzers['claude'].main_by_prepare(False, temperature, top_p)

    res = {
        'chat_gpt': {
            'compare_res': 0,
            'structure_res': 0,
            'corrected_success': 0,
            'first_success': 0,
            'error_count': 0,
            'execution_times': [],
        },
        'google_gemini': {
            'compare_res': 0,
            'structure_res': 0,
            'corrected_success': 0,
            'first_success': 0,
            'error_count': 0,
            'execution_times': [],
        },
        'claude': {
            'compare_res': 0,
            'structure_res': 0,
            'corrected_success': 0,
            'first_success': 0,
            'error_count': 0,
            'execution_times': [],
        }
    }

    for i in lists:
        # db = DatabaseConnection('chatbot-mssql:1433', 'sa', 'YourStrong!Passw0rd', f"{i}_answer")
        db = DatabaseConnection('chatbot-mssql:1433', 'sa', 'YourStrong!Passw0rd', f"CJDate")

        dump(f"---------------------------------------------")
        dump(f"{i}_answer:")
        dump(f"---------------------------------------------")
        standard_answer = load_file_content(f"./input/test/CJDate_with_DE_1/{i}_answer.txt")
        dump(f"參考答案的 SQL:")
        dump(f"{standard_answer}")
        standard_results = db.query(standard_answer)
        dump(f"參考答案的SQL撈取結果: {standard_results['data']}")
        dump(f"執行時間(ms): {standard_results['execution_time']} ms")

        for name, analyzer in analyzers.items():
            # time.sleep(5)

            error = False
            compare_res = -1
            # analyzer.main(i, None, temperature, top_p)
            dump(f"---------------------------------------------")
            answer_sql = analyzer.get_answer_sql(f"./output/{name}/CJDate_without_DE/1/{i}_{temperature}_{top_p}_question.json", 0)
            dump(f"{name} 預測的 SQL:")
            dump(f"{answer_sql}")

            result = db.query(answer_sql)

            if is_string(result['data']) == False:
                compare_res = compare_results(standard_results, False, result)

            if compare_res == 0:
                result['data'] = 'Wrong Answer'

            if is_string(result['data']):
                error = True
                res[name]['error_count'] += 1

                # time.sleep(5)

                # analyzer.main(i, error_format_text(result), temperature, top_p)
                answer_sql = analyzer.get_answer_sql(f"./output/{name}/CJDate_without_DE/1/{i}_{temperature}_{top_p}_question.json", 1)
                dump(f"錯誤後學習的 SQL:")
                dump(f"{answer_sql}")

            check_error = db.query(answer_sql)
            result = db.query(answer_sql, False)
            dump(f"SQL 撈取結果: {result['data']}")

            score = 0

            if is_string(check_error) == False:
                score = compare_sql_structure(standard_answer, answer_sql)

            res[name]['structure_res'] += score
            compare_res = compare_results(standard_results, True, result)

            if result['execution_time'] == None:
                result['execution_time'] = 0
                
            res[name]['execution_times'].append(result['execution_time'])

            error2 = False
            if name == 'google_gemini':
                error2 = 'There was an error in the sql just now' in analyzer.check_error_answer(f"./output/{name}/CJDate_without_DE/1/{i}_{temperature}_{top_p}_question.json")
                if error == False and error2 == True:
                    res[name]['error_count'] += 1

            if error == True or error2 == True:
                res[name]['corrected_success'] += compare_res

            res[name]['compare_res'] += compare_res

            if error == False and error2 == False:
                res[name]['first_success'] += compare_res

        db.close()

    return res

lists_length =len(lists)
result = analyze_and_compare(lists)

for analyzer, scores in result.items():
    dump(f"---------------------------------------------")
    dump(f"{analyzer} 預測的 SQL 分析:")

    compare_rate = scores['compare_res'] / lists_length * 100
    first_success = scores['first_success'] / lists_length * 100
    structure_similarity = scores['structure_res'] / lists_length * 100

    dump(f"首次準確率: {first_success:.2f}%")
    dump(f"準確率: {compare_rate:.2f}%")

    if scores['error_count'] != 0:
        structure_similarity = scores['corrected_success'] / scores['error_count'] * 100
        dump(f"錯誤改進率: {structure_similarity:.2f}%")
    else:
        dump(f"未發生錯誤")

    ves = calculate(lists_length, scores['execution_times'], 'CJDate')
    ves = ves * 100
    dump(f"VES: {ves:.2f}%")

dump(f"---------------------------------------------")