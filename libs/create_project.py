import io
import time
import streamlit as st
import os
from dotenv import load_dotenv
from libs.common import format_project_name, get_project_names, run_command
import libs.config as config
from contextlib import redirect_stdout
import asyncio
from graphrag.cli.initialize import initialize_project_at

load_dotenv()


def initialize_project(path):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    output = io.StringIO()

    try:
        with redirect_stdout(output):
            initialize_project_at(path)
        output_value = output.getvalue()
        st.success(output_value)
    finally:
        loop.close()


def overwrite_settings_yaml(root, new_project_name):
    settings_yaml = f"{root}/settings.yaml"
    template_settings_yaml = f"/app/template/setting.yaml"
    container_name = f"{config.app_name}_{new_project_name}"
    with open(template_settings_yaml, "r") as t:
        with open(settings_yaml, "w") as f:
            new_settings_yaml = t.read().replace(
                "container_name: default", f"container_name: {container_name}"
            )
            f.write(new_settings_yaml)


def create_project():
    project_name_list = get_project_names()
    new_project_value = "Just New Project"
    st.markdown("# New Project")
    today_hour = time.strftime("%Y%m%d%H", time.localtime())
    c1, c2, c3 = st.columns(3)
    with c1:
        new_project_name = st.text_input(
            "Please input name",
            value=today_hour,
            max_chars=30,
        )
    with c2:
        project_name_list.insert(0, new_project_value)
        copy_from_project_name = st.selectbox(
            "Copy from", project_name_list, key="create_from_project_name"
        )

    btn = st.button("Create", key="confirm", icon="🚀")
    if btn:
        formatted_project_name = format_project_name(new_project_name)

        if check_project_exists(formatted_project_name):
            st.error(f"Project {formatted_project_name} already exists.")
            return

        root = os.path.join("/app", "projects", formatted_project_name)

        try:
            if copy_from_project_name == new_project_value:
                initialize_project(path=root)
                overwrite_settings_yaml(root, formatted_project_name)
            else:
                copy_project(copy_from_project_name, formatted_project_name)
        except Exception as e:
            st.error(str(e))


def modify_project_prompt(
    formatted_project_name, file_name, search_text, project_language, type
):
    prompt_file = f"/app/projects/{formatted_project_name}/prompts/{file_name}"
    if os.path.exists(prompt_file):
        with open(prompt_file, "r") as f:
            prompt_content = f.read()
            new_prompt_content = prompt_content.replace(
                search_text,
                f"{search_text} You should use {project_language} for {type} description.",
            )
            with open(prompt_file, "w") as f:
                f.write(new_prompt_content)


def check_project_exists(formatted_project_name: str):
    return os.path.exists(f"/app/projects/{formatted_project_name}")


def copy_project(copy_from_project_name: str, formatted_project_name: str):
    run_command(
        f"cp -r '/app/projects/{copy_from_project_name}' '/app/projects/{formatted_project_name}'"
    )
    st.success(f"Project {copy_from_project_name} copied to {formatted_project_name}")
    time.sleep(3)
