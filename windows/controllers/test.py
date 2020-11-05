from selenium import webdriver
import time
import os
from extract_scripts import CompareWrapper

CompareWrapper(source_env="dev", target_env="prod")
