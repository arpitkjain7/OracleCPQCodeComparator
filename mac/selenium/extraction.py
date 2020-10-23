from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os


def pre_process(Input):
    output = Input.replace("/", "_")
    output = output.replace("?", "_")
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
    Localfilepath, Source_URL, Source_Username, Source_Password, Source_Env
):
    # param1 = webdriver.ChromeOptions()
    # param1.add_argument('headless')
    driver_Source = webdriver.Chrome(os.path.join(os.getcwd(), "setup", "chromedriver"))
    # driver_Source = webdriver.Chrome(
    #     "/Users/arpitkjain/Desktop/CPQ/cpq_code_comparison/setup/chromedriver"
    # )
    driver_Source.set_page_load_timeout(200)
    driver_Source.get(Source_URL)
    logging.info("Logging into Development Environment")
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


def Script_Extraction_Target(
    Localfilepath, Target_URL, Target_Username, Target_Password, Target_Env
):
    # param1 = webdriver.ChromeOptions()
    # param1.add_argument('headless')
    driver_Target = webdriver.Chrome(os.path.join(os.getcwd(), "setup", "chromedriver"))
    driver_Target.set_page_load_timeout(200)
    driver_Target.get(Target_URL)
    logging.info("Logging into Development Environment")
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

