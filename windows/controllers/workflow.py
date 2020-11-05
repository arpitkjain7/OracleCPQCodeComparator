# /***********************************************************
# Description : Program to extract all the scripts from CPQ enviorments (based on the option selected from UI) and compare the scripts.
#                Generate difference html files for all the changes which are in two env.
#                Generate detailed report with all the differences.
#                Generic script which can be used across all CPQ projects
# Pre-Requesits : 1. New folder with name "CPQCodeComparator" to be created in C folder.
#                2. Configuration file to be kept in this folder before running the code.
#                3. Need the UI page of CPQ to be generic Oracle CPQ login page.
# Name : Arpit Jain
# Email: arpitkjain@deloitte.com
# Change History : August 2019 Created
# **********************************************************/
import os
import time
import difflib
import logging
import xlsxwriter
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import threading
from controllers.get_env_config import get_config_data
from db_updates.update_db import create_batch, update_batch
from selenium.webdriver.common.keys import Keys

now = datetime.now()
todaysdate = now.strftime("%d%m%Y%H%M%S")
todaydatetime = now.strftime("%d-%m-%Y::%H:%M:%S")
List_of_new_files = []


def WriteToFile(ReportPath, DiffPath):
    logging.info("Generating Report")
    Report = ReportPath + "/CPQCodeVersioning.xlsx"
    workbook = xlsxwriter.Workbook(Report)
    Header_format = workbook.add_format(
        {"font_color": "black", "bold": 4, "underline": 1, "font_size": 16,}
    )
    worksheet = workbook.add_worksheet("CPQ_Report")
    worksheet.write_string("A1", "Modified Scripts", Header_format)
    worksheet.write_string("B1", "Navigation", Header_format)
    RowNum = 2
    for FileName in os.listdir(DiffPath):
        worksheet.write_string("A" + str(RowNum), FileName)
        worksheet.write_url(
            "B" + str(RowNum),
            DiffPath + "/" + FileName,
            string="Script",
            tip="Click here",
        )
        RowNum += 1
    workbook.close()
    return Report


def NewFiles(files):
    List_of_new_files.append(files)


def CompareTxtFiles(
    master_source_files, master_target_files, source_env, target_env, root_dir
):
    diff_path = root_dir + "/Differences/"
    doc_count = 0
    for target_file_name in master_target_files:
        target_path = master_target_files.get(target_file_name)
        source_path = master_source_files.get(target_file_name)
        target_file_location = os.path.join(
            diff_path, os.path.splitext(target_file_name)[0] + ".html"
        )
        if os.path.exists(target_file_location):
            target_file_location = os.path.join(
                diff_path,
                os.path.splitext(target_file_name)[0] + str(doc_count) + ".html",
            )
            doc_count += 1
        if type(source_path) != type(None):
            f1_lines = open(source_path).readlines()
            f2_lines = open(target_path).readlines()
            difference = difflib.HtmlDiff().make_file(
                f1_lines, f2_lines, source_env, target_env
            )
            for lines in difflib.unified_diff(f1_lines, f2_lines):
                if lines is not None:
                    difference_report = open(target_file_location, "w")
                    difference_report.write(difference)
                    difference_report.close()
            # Row_Num = WriteToFile(workbook=workbook, sheet=sheet, Name=target_file_name, ReportPath=root_dir,Href=diff_path + target_file_name + ".html", RowNum=Row_Num)
            # Row_Num += 1
        else:
            f2_lines = open(target_path).readlines()
            difference = difflib.HtmlDiff().make_file(
                f2_lines, "", source_env, target_env
            )
            difference_report = open(target_file_location, "w")
            difference_report.write(difference)
            difference_report.close()
            # Row_Num = WriteToFile(workbook=workbook, sheet=sheet, Name=target_file_name, ReportPath=root_dir, Href=diff_path + target_file_name + ".html", RowNum=Row_Num)
            # Row_Num += 1


master_files = {}
master = []
set_of_dir = []
master_source_files = {}
master_target_files = {}


def CompareFolders(source_path, target_path, source_env, target_env, root_dir):
    os.makedirs(root_dir + "/Differences", exist_ok=True)
    # logging.info("Comparing Scripts")
    for (root, subdirs, files) in os.walk(source_path, topdown=True):
        # print(root, subdirs, files)
        if len(subdirs) == 0:
            if len(files) != 0:
                # print(files[0])
                source_files = []
                dirPath = os.path.join(root, files[0])
                # print(dirPath)
                dirName = dirPath.split(os.path.sep)[-2]
                # print(dirName)
                list_of_dir_files = {dirName: files}
                master_files.update(list_of_dir_files)
                for txt_file in files:
                    txt_file_path = os.path.join(root, txt_file).replace(
                        os.path.sep, "/"
                    )
                    txt_file_name = txt_file_path.split("/")[-1]
                    master_source_files.update({txt_file_name: txt_file_path})
        else:
            for items in subdirs:
                set_of_dir.append(items)

    for (root, subdirs, files) in os.walk(target_path, topdown=True):
        # print(root, subdirs, files)
        if len(subdirs) == 0:
            if len(files) != 0:
                dirPath = os.path.join(root, files[0])
                dirName = dirPath.split(os.path.sep)[-2]
                masterFiles = master_files.get(dirName)
                target_files = files
                if type(masterFiles) == type(None):
                    for files in files:
                        NewFiles(files=files)
                else:
                    New_Files = set(masterFiles) - set(files)
                    # print(f"new files: {New_Files}")
                    for New_Files in New_Files:
                        List_of_new_files.append(New_Files)
                    for txt_file in files:
                        txt_file_path = os.path.join(root, txt_file).replace(
                            os.path.sep, "/"
                        )
                        txt_file_name = txt_file_path.split("/")[-1]
                        master_target_files.update({txt_file_name: txt_file_path})
    CompareTxtFiles(
        master_source_files, master_target_files, source_env, target_env, root_dir
    )


def pre_process(Input):
    output = Input.replace("/", "_")
    output = output.replace("?", "_")
    output = output.replace('"', "_")
    return output


def path_pre_process(path):
    return path.replace(os.path.sep, "/")


def FolderCreation(filepath, Env, Level0, Level1, Level2):
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    filepath = filepath + "/" + Env
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    if Level0 is not None:
        if not Level0.startswith("Copy"):
            filepath = filepath + "/" + Level0
            if not os.path.exists(filepath):
                os.mkdir(filepath)
            if Level1 is not None:
                if not Level1.startswith("Copy"):
                    filepath = filepath + "/" + Level1
                    if not os.path.exists(filepath):
                        os.mkdir(filepath)
                    if Level2 is not None:
                        if not Level2.startswith("Copy"):
                            filepath = filepath + "/" + Level2
                            if not os.path.exists(filepath):
                                os.mkdir(filepath)
                                return filepath
                            else:
                                return filepath
                        else:
                            return "Duplicate"
                    else:
                        return filepath
                else:
                    return "Duplicate"
            else:
                return filepath
        else:
            return "Duplicate"
    else:
        return filepath


def Script_Extraction_Source(
    batch_id,
    Localfilepath,
    Source_URL,
    Source_Username,
    Source_Password,
    Source_Env,
    headless,
):
    try:
        if headless:
            options = Options()
            options.add_argument("--headless")
            driver_Source = webdriver.Chrome(
                os.path.join(os.getcwd(), "setup", "chromedriver"),
                chrome_options=options,
            )
        else:
            driver_Source = webdriver.Chrome(
                os.path.join(os.getcwd(), "setup", "chromedriver")
            )
        # param1 = webdriver.ChromeOptions()
        # param1.add_argument('headless')

        # driver_Source = webdriver.Chrome(
        #     "/Users/arpitkjain/Desktop/CPQ/cpq_code_comparison/setup/chromedriver"
        # )
        print("Source env")
        print(Source_URL)
        driver_Source.set_page_load_timeout(200)
        driver_Source.get(Source_URL)
        logging.info("Logging into Source Environment")
        # Global Search on BML
        elem = driver_Source.find_element_by_xpath(
            "//label[@for='username']//following::input[1]"
        )
        elem.clear()
        elem.send_keys(Source_Username)
        elem = driver_Source.find_element_by_xpath(
            "//label[@for='psword']//following::input[1]"
        )
        elem.clear()
        elem.send_keys(Source_Password)
        elem = driver_Source.find_element_by_xpath("//*[text()='Log in']")
        elem.click()
        driver_Source.implicitly_wait(90)
        logging.info("Navigating to Admin screen")
        DevTools = EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div//h2[text()='Developer Tools']//following::a[text()='Global Search on BML']",
            )
        )
        BML = WebDriverWait(driver_Source, 30).until(DevTools)
        BML.click()

        Search = EC.element_to_be_clickable((By.XPATH, "//*[@name='search_string']"))
        Search_String = WebDriverWait(driver_Source, 30).until(Search)
        Search_String.send_keys("*")

        Search_button = driver_Source.find_element_by_xpath("//a[text()='Search']")
        Search_button.click()
        logging.info("Searching for scripts")
        Scripts = driver_Source.find_element_by_xpath("//table//form")
        NumOfScripts = Scripts.find_elements(By.TAG_NAME, "table")
        NumOfScripts = len(NumOfScripts)
        logging.info(f"Extracting {NumOfScripts} scripts from Dev")

        n = 3
        while n < NumOfScripts - 3:
            scriptHeadXPATH = "//table//form//table[" + str(n) + "]//tr[1]//td"
            scriptHead = driver_Source.find_element_by_xpath(scriptHeadXPATH)
            scriptHeadData = scriptHead.text
            scriptXPATH = "//table//form//table[" + str(n) + "]//tr[2]//td"
            script = driver_Source.find_element_by_xpath(scriptXPATH)
            scriptData = script.text
            scriptHeadData = scriptHeadData.split(":")
            ScriptNumber = pre_process(scriptHeadData[0]).strip()
            print(ScriptNumber)
            ScriptName = pre_process(scriptHeadData[-1]).strip()
            Master = scriptHeadData[0].split("      ")
            Level0 = pre_process(Master[1]).strip()
            m = 1
            level_dict = {}
            while m < len(scriptHeadData) - 1:
                Level = pre_process(scriptHeadData[m]).strip()
                level_dict.update({"Level" + str(m): Level})
                m += 1
            filepath = FolderCreation(
                Env=Source_Env,
                filepath=Localfilepath,
                Level0=Level0,
                Level1=level_dict.get("Level1"),
                Level2=level_dict.get("Level2"),
            )
            if filepath != "Duplicate":
                filename = filepath + "/" + ScriptName + ".txt"
                if os.path.exists(filename):
                    f = open(filename, mode="a+")
                    f.write("\n")
                    f.write(scriptData)
                else:
                    f = open(filename, mode="w+")
                    f.write(scriptData)
            n += 1
        driver_Source.close()
    except Exception as Error:
        update_batch(batch_id=str(batch_id), status="Error", error=str(Error))
        driver_Source.close()


def Script_Extraction_Prod(
    batch_id,
    Localfilepath,
    Target_URL,
    Target_Username,
    Target_Password,
    Target_Env,
    headless,
):

    if headless:
        options = Options()
        options.add_argument("--headless")
        driver_Prod = webdriver.Chrome(
            os.path.join(os.getcwd(), "setup", "chromedriver"), chrome_options=options,
        )
    else:
        driver_Prod = webdriver.Chrome(
            os.path.join(os.getcwd(), "setup", "chromedriver")
        )
    driver_Prod.set_page_load_timeout(2000)
    driver_Prod.get(Target_URL)
    logging.info("Logging into Target Environment")
    # accepting cookies
    cookie = WebDriverWait(driver_Prod, 100).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='onetrust-pc-btn-handler']")
        )
    )
    cookie.click()
    cookie_allow_all = WebDriverWait(driver_Prod, 100).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='accept-recommended-btn-handler']")
        )
    )
    cookie_allow_all.click()
    driver_Prod.implicitly_wait(200)
    # Global Search on BML
    element = WebDriverWait(driver_Prod, 100).until(
        EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
    )
    # elem = driver_Prod.find_element_by_xpath("//input[@name='username']")
    element.clear()
    element.send_keys(Target_Username)
    driver_Prod.implicitly_wait(200)
    next_button = WebDriverWait(driver_Prod, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
    )
    next_button.click()
    password = EC.element_to_be_clickable((By.XPATH, "//input[@name='password']",))
    password_input = WebDriverWait(driver_Prod, 30).until(password)
    password_input.clear()
    password_input.send_keys(Target_Password)
    checkbox = driver_Prod.find_element_by_xpath("//input[@class='form-check-input']")
    checkbox.send_keys(Keys.SPACE)
    driver_Prod.implicitly_wait(200)
    signIn = EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']",))
    signInButton = WebDriverWait(driver_Prod, 30).until(signIn)
    signInButton.send_keys("\n")
    logging.info("Navigating to Admin screen")
    driver_Prod.implicitly_wait(200)
    DevTools = EC.element_to_be_clickable(
        (
            By.XPATH,
            "//div//h2[text()='Developer Tools']//following::a[text()='Global Search on BML']",
        )
    )
    BML = WebDriverWait(driver_Prod, 30).until(DevTools)
    BML.click()

    Search = EC.element_to_be_clickable((By.XPATH, "//*[@name='search_string']"))
    Search_String = WebDriverWait(driver_Prod, 30).until(Search)
    Search_String.send_keys("*")
    Search_button = driver_Prod.find_element_by_xpath("//a[text()='Search']")
    Search_button.send_keys("\n")
    logging.info("Searching for scripts")
    Scripts = driver_Prod.find_element_by_xpath("//table//form")
    NumOfScripts = Scripts.find_elements(By.TAG_NAME, "table")
    NumOfScripts = len(NumOfScripts)
    logging.info(f"Extracting {NumOfScripts} scripts from Dev")

    n = 3
    while n < NumOfScripts - 3:
        scriptHeadXPATH = "//table//form//table[" + str(n) + "]//tr[1]//td"
        scriptHead = driver_Prod.find_element_by_xpath(scriptHeadXPATH)
        scriptHeadData = scriptHead.text
        scriptXPATH = "//table//form//table[" + str(n) + "]//tr[2]//td"
        script = driver_Prod.find_element_by_xpath(scriptXPATH)
        scriptData = script.text
        scriptHeadData = scriptHeadData.split(":")
        ScriptNumber = pre_process(scriptHeadData[0]).strip()
        print(ScriptNumber)
        ScriptName = pre_process(scriptHeadData[-1]).strip()
        Master = scriptHeadData[0].split("      ")
        Level0 = pre_process(Master[1]).strip()
        m = 1
        level_dict = {}
        while m < len(scriptHeadData) - 1:
            Level = pre_process(scriptHeadData[m]).strip()
            level_dict.update({"Level" + str(m): Level})
            m += 1
        filepath = FolderCreation(
            Env=Target_Env,
            filepath=Localfilepath,
            Level0=Level0,
            Level1=level_dict.get("Level1"),
            Level2=level_dict.get("Level2"),
        )
        if filepath != "Duplicate":
            filename = filepath + "/" + ScriptName + ".txt"
            if os.path.exists(filename):
                f = open(filename, mode="a+")
                f.write("\n")
                f.write(scriptData)
            else:
                f = open(filename, mode="w+")
                f.write(scriptData)
        n += 1
    driver_Prod.close()


# except Exception as Error:
#     update_batch(batch_id=str(batch_id), status="Error", error=str(Error))
#     driver_Prod.close()


def Script_Extraction_Target(
    batch_id,
    Localfilepath,
    Target_URL,
    Target_Username,
    Target_Password,
    Target_Env,
    headless,
):
    try:
        print("Target env")
        print(Target_URL)
        if headless:
            options = Options()
            options.add_argument("--headless")
            driver_Target = webdriver.Chrome(
                os.path.join(os.getcwd(), "setup", "chromedriver"),
                chrome_options=options,
            )
        else:
            driver_Target = webdriver.Chrome(
                os.path.join(os.getcwd(), "setup", "chromedriver")
            )
        driver_Target.set_page_load_timeout(200)
        driver_Target.get(Target_URL)
        logging.info("Logging into Target Environment")
        # Global Search on BML
        elem = driver_Target.find_element_by_xpath(
            "//label[@for='username']//following::input[1]"
        )
        elem.clear()
        elem.send_keys(Target_Username)
        elem = driver_Target.find_element_by_xpath(
            "//label[@for='psword']//following::input[1]"
        )
        elem.clear()
        elem.send_keys(Target_Password)
        elem = driver_Target.find_element_by_xpath("//*[text()='Log in']")
        elem.click()
        driver_Target.implicitly_wait(90)
        logging.info("Navigating to Admin screen")
        DevTools = EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div//h2[text()='Developer Tools']//following::a[text()='Global Search on BML']",
            )
        )
        BML = WebDriverWait(driver_Target, 30).until(DevTools)
        BML.click()

        Search = EC.element_to_be_clickable((By.XPATH, "//*[@name='search_string']"))
        Search_String = WebDriverWait(driver_Target, 30).until(Search)
        Search_String.send_keys("*")

        Search_button = driver_Target.find_element_by_xpath("//a[text()='Search']")
        Search_button.click()
        logging.info("Searching for scripts")
        Scripts = driver_Target.find_element_by_xpath("//table//form")
        NumOfScripts = Scripts.find_elements(By.TAG_NAME, "table")
        NumOfScripts = len(NumOfScripts)
        logging.info(f"Extracting {NumOfScripts} scripts from Dev")

        n = 3
        while n < NumOfScripts - 3:
            scriptHeadXPATH = "//table//form//table[" + str(n) + "]//tr[1]//td"
            scriptHead = driver_Target.find_element_by_xpath(scriptHeadXPATH)
            scriptHeadData = scriptHead.text
            scriptXPATH = "//table//form//table[" + str(n) + "]//tr[2]//td"
            script = driver_Target.find_element_by_xpath(scriptXPATH)
            scriptData = script.text
            scriptHeadData = scriptHeadData.split(":")
            ScriptNumber = pre_process(scriptHeadData[0]).strip()
            print(ScriptNumber)
            ScriptName = pre_process(scriptHeadData[-1]).strip()
            Master = scriptHeadData[0].split("      ")
            Level0 = pre_process(Master[1]).strip()
            m = 1
            level_dict = {}
            while m < len(scriptHeadData) - 1:
                Level = pre_process(scriptHeadData[m]).strip()
                level_dict.update({"Level" + str(m): Level})
                m += 1
            filepath = FolderCreation(
                Env=Target_Env,
                filepath=Localfilepath,
                Level0=Level0,
                Level1=level_dict.get("Level1"),
                Level2=level_dict.get("Level2"),
            )
            if filepath != "Duplicate":
                filename = filepath + "/" + ScriptName + ".txt"
                if os.path.exists(filename):
                    f = open(filename, mode="a+")
                    f.write("\n")
                    f.write(scriptData)
                else:
                    f = open(filename, mode="w+")
                    f.write(scriptData)
            n += 1
        driver_Target.close()
    except Exception as Error:
        update_batch(batch_id=str(batch_id), status="Error", error=str(Error))
        driver_Target.close()


# def clone(GIT_url, localrepo):
#     from git import Repo

#     Repo.clone_from(GIT_url, localrepo)


# def moveFiles(source, target):
#     print(f"source {source}")
#     print(f"target {target}")
#     new_target = target + "/" + Req_id
#     # if not os.path.isdir(new_target):
#     #    os.mkdir(new_target)
#     files = os.listdir(source)
#     for f in files:
#         try:
#             shutil.copytree(source, new_target)
#             print("Success")
#         except shutil.Error as e:
#             print("Directory not copied. Error: %s" % e)
#         except OSError as e:
#             print("Directory not copied. Error: %s" % e)


# def pullrequest(localrepo):
#     if os.path.isdir(localrepo):
#         repo = git.Repo(localrepo)
#         repo.remotes.origin.fetch()
#         repo.remotes.origin.pull()
#         status = repo.git.status()
#         print("Success")
#         print(status)
#     else:
#         print("Error")
#         print("Not a valid path. Please check the path provided for local repository")


# def commitrequest(localrepo):
#     import git

#     repo = git.Repo(localrepo)
#     repo.git.add("--all")
#     repo.git.commit("-m", "Automation Tool")
#     repo.git.push("origin")
#     status = repo.git.status()
#     print("Success")
#     print("Changes pushed successfully to remote repository")


# def GIT():
#     source = tkvar1.get()
#     SourceParam = pd.DataFrame(df, columns=[source]).values.tolist()
#     filepath = path_pre_process(SourceParam[3][0])
#     GIT_url = SourceParam[4][0]
#     filepath = filepath + "/" + Req_id
#     GIT_Path = path_pre_process(e2.get())
#     GIT_Checkbox = CheckBox.get()
#     # GIT_url = "https://github.com/jainara1012/CPQ_Code_Versioning.git"
#     if GIT_Checkbox != 0 and GIT_Path != None:
#         try:
#             print("GIT pull started")
#             pullrequest(localrepo=GIT_Path)
#         except:
#             the_type, the_value, the_traceback = sys.exc_info()
#             if str(the_type) == "<class 'git.exc.InvalidGitRepositoryError'>":
#                 # print(the_type)
#                 # print(the_value)
#                 print(
#                     "Repository is not a GIT repository. Clonning the repository on provided path"
#                 )
#                 clone(GIT_url=GIT_url, localrepo=GIT_Path)
#                 print("Success")
#         moveFiles(source=filepath, target=GIT_Path)
#         print("Files moved to GIT repository")
#         print("Commit started")
#         commitrequest(localrepo=GIT_Path)
#         popupmsg = "Files commited to GIT repository"
#         messagebox.showinfo(title="Commit Successful", message=popupmsg)
#     else:
#         popupmsg = "Provide GIT path and tick the checkbox"
#         messagebox.showinfo(title="Invalid File Path", message=popupmsg)


def CompareWrapper(source_env: str, target_env: str, headless: bool):
    try:
        batch_id = int(datetime.now().timestamp() * 1000)
        create_batch(batch_id=batch_id)
        SourceParam = get_config_data(source_env)
        TargetParam = get_config_data(target_env)
        Source_URL = SourceParam.get("url") + "/admin/"
        Source_Username = SourceParam.get("username")
        Source_Password = SourceParam.get("password")
        Target_URL = TargetParam.get("url") + "/admin/"
        Target_Username = TargetParam.get("username")
        Target_Password = TargetParam.get("password")
        log_file_path = os.path.join(os.getcwd(), "logs", "LogFile.log")
        logging.basicConfig(filename=log_file_path, level=logging.DEBUG, filemode="w")
        output_dir_path = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir_path, exist_ok=True)
        if os.path.isdir(output_dir_path):
            output_batch_path = os.path.join(output_dir_path, str(batch_id))
            if source_env.lower() in ("prod", "production"):
                source_thread = threading.Thread(
                    target=Script_Extraction_Prod,
                    args=(
                        batch_id,
                        output_batch_path,
                        Source_URL,
                        Source_Username,
                        Source_Password,
                        source_env,
                        headless,
                    ),
                )
            else:
                source_thread = threading.Thread(
                    target=Script_Extraction_Source,
                    args=(
                        batch_id,
                        output_batch_path,
                        Source_URL,
                        Source_Username,
                        Source_Password,
                        source_env,
                        headless,
                    ),
                )
            if target_env.lower() in ("prod", "production"):
                target_thread = threading.Thread(
                    target=Script_Extraction_Prod,
                    args=(
                        batch_id,
                        output_batch_path,
                        Target_URL,
                        Target_Username,
                        Target_Password,
                        target_env,
                        headless,
                    ),
                )
            else:
                target_thread = threading.Thread(
                    target=Script_Extraction_Target,
                    args=(
                        batch_id,
                        output_batch_path,
                        Target_URL,
                        Target_Username,
                        Target_Password,
                        target_env,
                        headless,
                    ),
                )
            logging.info(
                f"Comparing {target_env} environment with {source_env} environment"
            )
            source_thread.start()
            logging.info("Thread 1 started")
            target_thread.start()
            logging.info("Thread 2 started")
            source_thread.join()
            logging.info("Thread 1 ended")
            target_thread.join()
            logging.info("Thread 2 ended")
            source_path = os.path.join(output_batch_path, source_env)
            target_path = os.path.join(output_batch_path, target_env)
            CompareFolders(
                source_path=source_path,
                target_path=target_path,
                source_env=source_env,
                target_env=target_env,
                root_dir=output_batch_path,
            )
            Report = WriteToFile(
                ReportPath=output_batch_path,
                DiffPath=os.path.join(output_batch_path, "Differences"),
            )
        update_batch(batch_id=str(batch_id), status="Completed")

    except Exception as Error:
        update_batch(batch_id=str(batch_id), status="Error", error=str(Error))

