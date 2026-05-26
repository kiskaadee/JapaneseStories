from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseModel

# -- Enums and Helpers


class PartOfSpeechEnum(str, Enum):
    NOUN = "noun"
    GODAN_VERB = "godan_verb"  # e.g., kaku
    ICHIDAN_VERB = "ichidan_verb"  # e.g., taberu
    IRREGULAR_VERB = "irregular_verb"  # e.g., suru, kuru
    TRUE_ADJ = "true_adj"  # -i adjectives
    NA_ADJ = "na_adj"  # -na adjectives
    ADVERB = "adverb"
    PARTICLE = "particle"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    PRONOUN = "pronoun"


class CollectionBase(BaseModel):
    """Highest level container (e.g., 'Japanese Language Learning' or Okinawa Trip)"""

    name: str
    description: str


class Collection(CollectionBase):
    id: int
    user_id: int


class Resource(BaseModel):
    label: str  # e.g., "Urashima Taro Audio"
    # e.g., "https://tuttlepublishing.com/..." [cite: 5]
    url: AnyHttpUrl


class TopicBase(BaseModel):
    """A sub-category within a collection (e.g., 'Folktale Vocabulary')"""

    collection_id: int
    title: str
    description: Optional[str] = ""


class Topic(TopicBase):
    id: int


class TermBase(BaseModel):
    """The actual glossary entry"""

    topic_id: int
    word: str  # e.g., "人"
    furigana: str  # e.g., "ひと"
    romaji: str  # e.g., "hito"
    part_of_speech: PartOfSpeechEnum  # e.g., "noun"
    semantic_category: str  # e.g., "folktale", "nature", "emotion"
    is_mimetic: bool = False  # e.g.,
    explanation: Optional[str] = ""  # e.g.,
    examples: List[str] = []  # e.g.,
    resources: List[Resource] = []

    # Active recall (SM-2 algorith fields)
    interval: int = 0  # Days until the next review
    ease_factor: float = 2.5  # SM-2 multiplier (def: 2.5)
    next_review_date: Optional[datetime] = None


class TermCreate(TermBase):
    pass


class Term(TermBase):
    id: int
