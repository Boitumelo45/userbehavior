import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Read environment variables"""
    DAILY_EXPENSES: str
    USER_BEHAVIOR_URL: str
    WEEKLY_EXPENSES: str
    MONTHLY_EXPENSES: str
    PREDICTIVE_EXPENSES: str # this was omitted/extra bonus if you found it
    CATEGORY_EXPENSES: str
    
    class Config:
        with open('.env', 'r') as f:
            lines = f.readlines()
            for line in lines:
                print(line)
        env_file = ".env"

settings = Settings()
print(settings) # debug