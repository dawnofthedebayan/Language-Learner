import json
import datetime
from typing import List

from config import TOPICS_PATH
import random

def load_topics(path: str = TOPICS_PATH) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_topic_of_day(topics: List[str]) -> str:
    
    index = random.randint(0, len(topics) - 1)
    return topics[index]
