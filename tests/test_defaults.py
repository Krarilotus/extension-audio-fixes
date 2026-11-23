from pathlib import Path
import re

import pytest
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
OPTIONS = ('startup-sfx-volume', 'video-fx-volume', 'positional-audio')


def test_options_default_off_with_unchanged_urls():
    text = (ROOT / 'options.yml').read_text(encoding='utf-8')
    assert re.findall(r'^\s+url: (\S+)$', text, re.M) == [f'audio-fixes.{name}' for name in OPTIONS]
    assert re.findall(r'^\s+value: (\S+)$', text, re.M) == ['false'] * len(OPTIONS)


@pytest.mark.parametrize('config', ({}, dict.fromkeys(OPTIONS, False)))
def test_missing_or_false_options_install_nothing(config):
    lua = LuaRuntime()
    required = []
    lua.globals().require = lambda name: required.append(name) or lua.table_from({'enable': lambda: None})
    init = lua.execute((ROOT / 'init.lua').read_text())
    init.enable(init, lua.table_from(config))
    assert required == []
