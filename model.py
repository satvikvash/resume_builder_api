from pydantic import BaseModel
from typing import List

# Socials
class Socials(BaseModel):
    platform_name: str
    link_to_profile: str

# Profile
class Profile(BaseModel):
    full_name: str
    phone_no: str
    email: str
    socials: List[Socials]

# Education
class Education(BaseModel):
    name: str
    degree: str
    start_year: str
    end_year: str
    grade: str

# Description for Experience, Projects
class Description(BaseModel):
    points: str

# Experience
class Experience(BaseModel):
    position: str
    company_name: str
    location: str
    start_date: str
    end_date: str
    description: List[Description]

# Project
class Project(BaseModel):
    name: str
    tech_stack: str
    link_to_project: str
    description: List[Description]

# Language
class Language(BaseModel):
    name: str

# Skills
class Skills(BaseModel):
    tech_skills: List[Language]
    frameworks: List[Language]
    developer_tools: List[Language]
    libraries: List[Language]

class ResumeData(BaseModel):
    profile: Profile
    education: List[Education]
    experience: List[Experience]
    project: List[Project]
    skills: Skills
