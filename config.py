import os

class Config:
    DEBUG = False
    DEVELOPMENT = False
    SCRAPE_URL = ""
    NUM_OF_PAGES = 0


class ProductionConfig(Config):
    pass

class StagingConfig(Config):
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SCRAPE_URL = "https://www.memoryexpress.com/Category/VideoCards?FilterID=b9021f59-29a3-73a7-59b5-125edab939f2&PageSize=120"
    NUM_OF_PAGES = 3