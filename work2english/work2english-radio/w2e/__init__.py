"""Work2English core package.

Layered modules shared by all entry points (run.py / server.py /
radio_service.py / feishu_collect.py). Foundation modules (io_utils, runtime,
config) are import-safe before the venv switch because they depend only on the
stdlib + (config) pyyaml, which entry points load after ensure_venv_python().
"""
