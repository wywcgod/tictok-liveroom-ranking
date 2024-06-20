import re
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy as AppiumBy
from appium import webdriver
import time
import datetime
import pymysql

# 输出结果每两行合成一行
def merge_every_two_lines(text_list):
    merged_list = []
    # 使用迭代器来遍历列表，每次步进2
    for i in range(0, len(text_list), 2):
        # 合并当前行和下一行（如果存在）
        merged_line = text_list[i]
        if i + 1 < len(text_list):
            merged_line += ", " + text_list[i + 1]
        merged_list.append(merged_line)
    return merged_list

# 去重方法
def remove_duplicates_ordered(text_list):
    unique_list = []
    seen = set()
    for item in text_list:
        if item not in seen:
            unique_list.append(item)
            seen.add(item)
    return unique_list

# 四位数前加小数点
def format_list(input_list):
    for i in range(len(input_list)):
        parts = input_list[i].split('\t')  # 请确保这里的分隔符是正确的
        # 检查parts[2]是否是四位数且是整数
        if parts[2].isdigit() and len(parts[2]) == 4:
            parts[2] = "0." + parts[2]
        input_list[i] = '\t'.join(parts)

# appium初始化参数
caps = {}
caps["platformName"] = "Android"
caps["platformVersion"] = "13"
caps["deviceName"] = "ANY_AN00"
caps["appPackage"] = "com.ss.android.ugc.aweme"
caps["appActivity"] = "com.ss.android.ugc.aweme.splash.SplashActivity"
caps["resetKeyboard"] = True
#caps["unicodeKeyboard"] = True
caps["noReset"] = True
caps["newCommandTimeout"] = 600

#数据库参数
db_config = {
            'host': '192.168.1.245',
            'user': 'bi_bytegame_f',
            'passwd': "123456",
            'db': 'bi_bytegame',
            'charset': 'utf8mb4'
}

# date
current_date = datetime.datetime.now().date()
print(current_date)

# time
current_time = time.localtime()
current_hour = current_time.tm_hour
next_hour = (current_hour + 1) % 24
time_range = "{:02d}:00 ~ {:02d}:00".format(current_hour, next_hour)
print(time_range)

# 检测库中是否有当前小时数据
try:
    # 使用with语句确保资源正确关闭
    with pymysql.connect(**db_config) as conn:
        with conn.cursor() as cur:
            # 使用参数化查询来避免SQL注入风险
            sql = "select date,time from bytegame where `date` = %s and  time= %s"
            cur.execute(sql, (current_date, time_range))
            result = cur.fetchone()
            # conn.commit()  # 不要忘记提交事务
# except pymysql.MySQLError as e:
#     print("Error: ", e)
finally:
    pass
if not result:
    #连接appium
    driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", caps)
    time.sleep(6)
    # driver.tap([(227, 2244)], 200)
    #el1 = driver.find_element(by=AppiumBy.ID, value="com.ss.android.ugc.aweme:id/hcu")
    #el1.click()
    driver.tap([(997, 156)], 200)
    time.sleep(4)
    el2 = driver.find_element(by=AppiumBy.ID, value="com.ss.android.ugc.aweme:id/et_search_kw")
    el2.send_keys("弹幕游戏直播")
    time.sleep(4)
    driver.tap([(987, 156)], 200)
    #el3 = driver.find_element(by=AppiumBy.ID, value="com.ss.android.ugc.aweme:id/yqq")
    #el3.click()
    time.sleep(4)
    # 点开第一个直播
    driver.tap([(348, 1138)], 200)
    time.sleep(6)
    # 点击空白页面，避免超长直播弹窗
    driver.tap([(720, 1522)], 200)
    time.sleep(6)
    # 点击弹幕排行榜
    driver.tap([(208, 279)], 200)
    time.sleep(8)
    # 点击主播榜
    driver.tap([(95, 727)], 200)
    time.sleep(8)

    start_x = 540
    start_y = 1985
    end_x = 540
    end_y = 1400
    # 1700
    # 设置一个标志位，用于判断何时停止滑动
    stop_swiping = False

    # 存储上一个元素文本
    prev_text = ""

    # 初始化一个列表来存储结果
    result_list = []

    while not stop_swiping:
        # 获取当前屏幕上的元素
        elements = driver.find_elements(By.CLASS_NAME, "com.lynx.tasm.behavior.ui.LynxFlattenUI")

        # 如果没有找到元素，可能是到底了，可以停止滑动
        if not elements:
            stop_swiping = True
        else:
            # 遍历当前屏幕上的所有元素的文本
            for element in elements:
                text = element.text
                # 如果文本包含“当前主播”，则去除这部分内容
                if "当前主播" in text or "排名中" in text or "已选中" in text or "玩法榜，按钮" in text or "支持" in text:
                    continue
                result_list.append(text)  # 将结果添加到集合中
                # 检查是否包含“第51名”，如果包含则设置停止标志
                if "第51名" in text:
                    stop_swiping = True
                    break

            # 如果还没有找到“第51名”，则滑动屏幕以获取更多元素
            if not stop_swiping:
                driver.swipe(start_x, start_y, end_x, end_y, 1000)
                # 等待页面加载
                time.sleep(6)
    driver.close_app()

    # 原始数据
    for text in result_list:
        print(text)

    processed_list = []

    # 遍历原始文本列表
    index = 0
    while index < len(result_list):
        # 如果是最后一行并且包含“当前”，则直接忽略
        if index == len(result_list) - 1 and "当前" in result_list[index]:
            break
        # 如果当前文本包含“当前”且下一个文本不包含“比赛”或者“对战”，则跳过当前文本
        if "当前" in result_list[index] and index < len(result_list) - 1 and (
                "当前" in result_list[index + 1]):
            index += 1  # 只跳过当前文本
        else:
            processed_list.append(result_list[index])  # 将当前文本添加到处理后的列表中
            if index < len(result_list) - 1:  # 检查是否已经到达列表末尾
                processed_list.append(result_list[index + 1])  # 将下一个文本添加到处理后的列表中
            index += 2

    # 现在调用函数来合并每两行为一行
    merged_list = merge_every_two_lines(processed_list)
    # 现在调用函数来去重
    no_duplicates_list_ordered = remove_duplicates_ordered(merged_list)

    no_duplicates_list_ordered_1 = []

    # 去除指定词语处理并输出结果
    for results in no_duplicates_list_ordered:
        final_result = (results.replace("'", "").replace("\\", "").replace(",直播中", "\t").replace(",未在直播", "\t")
                        .replace(" ", "")
                        .replace(",对战,", "").replace(",角力,", "").replace(",攻防,", "").replace(",竞速,", "")
                        .replace(",比赛,", "").replace(",涂色,", "").replace(",闯关,", "").replace(",养成,", "")
                        .replace(",乱斗,", "").replace(",整蛊,", "").replace(",音舞,", "").replace(",消除,", "")
                        .replace(",消除,", "").replace("，按钮", "").replace(",,", ""))
        # 使用正则表达式去除“第1名”、“第2名”中的数字1和2
        final_result = re.sub(r',第\d+名,', '\t', final_result)
        final_result = re.sub(r"当前(\d+\.?\d*)万", r"\1", final_result)
        final_result = final_result.replace("当前", "")

        print(final_result)
        # 分割最终结果
        parts = final_result.split("\t")
        # 按照新的顺序重新组合信息
        # 注意：这里假设parts的结构是 [主播名字, 观众人数, 对战/比赛内容]
        # 如果实际结构不同，你可能需要调整索引
        reordered_result = f"{parts[2]}\t{parts[0]}\t{parts[1]}"
        no_duplicates_list_ordered_1.append(reordered_result)

        # 输出处理后的结果
        # print(reordered_result)
    format_list(no_duplicates_list_ordered_1)
    for text in no_duplicates_list_ordered_1:
        print(text)
    # 去重后的结果
    for text in no_duplicates_list_ordered:
        print(text)

    # 输出结果到文件
    output_file_path = "tiktok_results.txt"  # 定义输出文件的路径
    with open(output_file_path, 'a+', encoding='utf-8') as file:  # 使用追加模式打开文件
        file.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '   aaa\n')
        # 新增排名
        for index, text in enumerate(no_duplicates_list_ordered_1, start=1):  # Start the index from 1
            file.write(text + "\n")  # 写入文件并添加换行符
            # 写入库
            try:
                parts = text.split("\t")
                # 使用with语句确保资源正确关闭
                with pymysql.connect(**db_config) as conn:
                    with conn.cursor() as cur:
                        # 使用参数化查询来避免SQL注入风险
                        sql = "INSERT INTO bytegame (date, time, gameplay_name, anchor_name, sound_wave_number, ranking) VALUES (%s, %s, %s, %s, %s, %s)"
                        cur.execute(sql, (current_date, time_range, parts[0], parts[1], parts[2], index))
                        conn.commit()  # 不要忘记提交事务
            # except pymysql.MySQLError as e:
            #     print("Error: ", e)
            finally:
                pass


