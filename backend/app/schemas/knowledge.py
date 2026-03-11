from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime, date


# -- DRIVER ----------------------------------------
class DriverBase(BaseModel):
    name: str
    version: str
    operating_system: str
    architecture: str
    download_url: str
    release_date: Optional[date] = None

class DriverCreate(DriverBase):
    product_id: str

class DriverUpdate(BaseModel):
    version: Optional[str] = None
    download_url: Optional[str] = None
    is_active: Optional[bool] = None

class DriverResponse(DriverBase):
    id: str
    product_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -- KNOWN ISSUE -----------------------------------
class KnownIssueBase(BaseModel):
    title: str
    error_code: Optional[str] = None
    description: str
    solution_steps: List[Any] = []
    category: str
    difficulty: str

class KnownIssueCreate(KnownIssueBase):
    product_id: Optional[str] = None

class KnownIssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    solution_steps: Optional[List[Any]] = None
    is_active: Optional[bool] = None

class KnownIssueResponse(KnownIssueBase):
    id: str
    product_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -- FAQ -------------------------------------------
class FAQBase(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None

class FAQCreate(FAQBase):
    pass

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class FAQResponse(FAQBase):
    id: str
    times_used: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -- KNOWLEDGE EMBEDDING ---------------------------
class KnowledgeEmbeddingResponse(BaseModel):
    id: str
    source_type: str
    source_id: str
    content_text: str
    created_at: datetime

    class Config:
        from_attributes = True
