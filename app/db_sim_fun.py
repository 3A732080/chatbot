from helper_fun import clean_json_string, dd, dump
import sqlparse
from sqlparse.sql import (IdentifierList, Identifier, Where, TokenList, 
                          Comparison, Function, Having, Parenthesis)
from sqlparse.tokens import Keyword, DML, Whitespace, Name, Comparison, Operator, CTE, Punctuation
import math

def extract_clauses(parsed):
    """提取 SQL 查詢的主要子句。"""
    clauses = {
        'SELECT': [],
        'FROM': [],
        'JOIN': [],
        'WHERE': [],
        'GROUP BY': [],
        'HAVING': [],
        'ORDER BY': []
    }
    current_clause = ''

    for token in parsed.tokens:
        if isinstance(token, TokenList):
            if any(token.ttype is Keyword for token in token.flatten()):
                sub_clauses = extract_clauses(token)
                for clause, elements in sub_clauses.items():
                    clauses[clause].extend(elements)
            continue

        if token.ttype is Keyword:
            token_value = token.value.upper()
            if token_value in clauses:
                current_clause = token_value
        elif current_clause and token.ttype not in [Whitespace, Keyword, Punctuation]:
            clauses[current_clause].append(str(token).strip())

    return clauses

def normalize_element(element):
    """對比較元素進行標準化。"""
    return element.lower().replace(" ", "")

def compare_elements(set1, set2):
    """比較兩個元素集合，考慮標準化後的相似度。"""
    normalized_set1 = {normalize_element(e) for e in set1}
    normalized_set2 = {normalize_element(e) for e in set2}
    return normalized_set1 == normalized_set2

def compare_clauses(clauses1, clauses2):
    """比較兩個查詢中的子句，並計算相似度分數。"""
    score = 0
    total_clauses = len(clauses1)

    for clause in clauses1:
        set1 = set(clauses1[clause])
        set2 = set(clauses2.get(clause, []))

        if compare_elements(set1, set2):
            score += 1
        elif set1 & set2:
            score += 0.5

    return score / total_clauses

def compare_sql_structure(sql1, sql2):
    """比較兩個 SQL 查詢的結構相似度。"""
    parsed1 = sqlparse.parse(sql1)[0]
    parsed2 = sqlparse.parse(sql2)[0]

    clauses1 = extract_clauses(parsed1)
    clauses2 = extract_clauses(parsed2)

    score = compare_clauses(clauses1, clauses2)

    return float(score)

def compare_results(standard, show, result):
    res = 1

    if set(standard['data']['column']) == set(result['data']['column']) and len(result['data']['value']) == len(standard['data']['value']):
        for row in result['data']['value']:
            if row not in standard['data']['value']:
                res = 0

                break
    else:
        res = 0

    if show == False:
        return res

    if res == 0:
        dump(f"SQL 預測結果:不正確")
    else:
        dump(f"SQL 預測結果:正確")

    if result['execution_time'] != None:
        dump(f"執行時間(毫秒): {result['execution_time']} ms")
    if result['execution_time'] == None:
        dump(f"執行時間(毫秒): 0 ms")

    return res

def calculate(lists_length, execution_time, db_name):
    if db_name == 'LeetCode':
        ans_time = [17, 10, 4, 10, 10, 10, 17, 100, 13]

    if db_name == 'CJDate':
        ans_time = [57, 40, 30, 33, 56, 37, 47, 46, 13]

    va_result = []
    sqrt_result = []
    for i in range(len(execution_time)):
        if execution_time[i] == 0:
            va_result.append(0)
        else:
            va_result.append(1)
        ans = execution_time[i]
        model = ans_time[i]
        result = math.sqrt(ans / model) 
        rounded_result = round(result, 4) 
        sqrt_result.append(rounded_result)

    ves_scores = [a * b for a, b in zip(va_result, sqrt_result)]

    total_ves_score = sum(ves_scores)

    ves = round(total_ves_score / lists_length, 4)

    return ves