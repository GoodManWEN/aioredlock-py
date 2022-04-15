import os , sys
sys.path.append(os.getcwd())
import pytest
from aioredlock_py import *

@pytest.mark.asyncio
async def test_import():
    ...