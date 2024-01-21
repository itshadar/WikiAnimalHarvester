from pydantic import BaseModel


class PageQueueItem(BaseModel):
    """
    Pydantic schema for items in the page_queue.
    """
    page_url: str
    page_name: str


class ImageQueueItem(BaseModel):
    """
    Pydantic schema for items in the image_queue.
    """
    image_url: str
    image_name: str
