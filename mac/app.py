from fastapi import FastAPI

# from cpq_code_comparison.controllers.get_env_config import get_config_data
from controllers.get_env_config import get_config_data
from controllers.workflow import CompareWrapper, CompareFolders, WriteToFile

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/env_config/{env_name}")
def get_env_config(env_name: str):
    data = get_config_data(env=env_name)
    return {"env_data": data}


@app.post("/extract_scripts")
def extract_scripts(source_env_name: str, target_env_name: str, headless: bool = True):
    CompareWrapper(
        source_env=source_env_name, target_env=target_env_name, headless=headless
    )
    return "success"


@app.post("/compare")
def compare(
    source_path: str,
    target_path: str,
    source_env: str,
    target_env: str,
    output_batch_path: str,
):
    CompareFolders(
        source_path=source_path,
        target_path=target_path,
        source_env=source_env,
        target_env=target_env,
        root_dir=output_batch_path,
    )
    return "success"


@app.post("/write")
def write_to_file(
    ReportPath: str, DiffPath: str,
):
    WriteToFile(
        ReportPath=ReportPath, DiffPath=DiffPath,
    )
    return "success"
