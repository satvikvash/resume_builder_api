from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from model import ResumeData, Education, Experience, Project
from typing import List
import subprocess
import os

app = FastAPI()


origins = [
    "http://localhost:5173",  # Vite default dev server port
    "https://resume-builder-api-hfwb.onrender.com", # Add the production domain here when you deploy
    ""
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the Pydantic models here (Profile, Education, Experience, etc.)
# ...

@app.get("/")
def read_root():
    return {"message": "Hello, This is the Resume Buidler API working as expected!"}


@app.post("/generate-resume/")
async def generate_resume(resume_data: ResumeData):
    latex_code = generate_latex(resume_data)
    pdf_path = compile_latex_to_pdf(latex_code)
    
    if pdf_path:
        return FileResponse(pdf_path, media_type="application/pdf", filename="resume.pdf")
    else:
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

def generate_latex(resume_data: ResumeData) -> str:
    # Generate the LaTeX code using the data provided in resume_data
    # Use concatenation instead of f-strings within LaTeX commands
    socials_str = " $|$ ".join([
        "\\href{" + social.link_to_profile + "}{" + "\\underline{" + social.platform_name + "}}"
        for social in resume_data.profile.socials
    ])

    latex_preamble = (
        "\\documentclass[letterpaper,11pt]{article}\n\n"
        "\\usepackage{latexsym}\n"
        "\\usepackage[empty]{fullpage}\n"
        "\\usepackage{titlesec}\n"
        "\\usepackage{marvosym}\n"
        "\\usepackage[usenames,dvipsnames]{color}\n"
        "\\usepackage{verbatim}\n"
        "\\usepackage{enumitem}\n"
        "\\usepackage[hidelinks]{hyperref}\n"
        "\\usepackage{fancyhdr}\n"
        "\\usepackage[english]{babel}\n"
        "\\usepackage{tabularx}\n"
        "\\input{glyphtounicode}\n\n"
        "\\pagestyle{fancy}\n"
        "\\fancyhf{}\n"
        "\\fancyfoot{}\n"
        "\\renewcommand{\\headrulewidth}{0pt}\n"
        "\\renewcommand{\\footrulewidth}{0pt}\n\n"
        "\\addtolength{\\oddsidemargin}{-0.5in}\n"
        "\\addtolength{\\evensidemargin}{-0.5in}\n"
        "\\addtolength{\\textwidth}{1in}\n"
        "\\addtolength{\\topmargin}{-.5in}\n"
        "\\addtolength{\\textheight}{1.0in}\n\n"
        "\\urlstyle{same}\n\n"
        "\\raggedbottom\n"
        "\\raggedright\n"
        "\\setlength{\\tabcolsep}{0in}\n\n"
        "\\titleformat{\\section}{\n"
        "  \\vspace{-4pt}\\scshape\\raggedright\\large\n"
        "}{}{0em}{}[\\color{black}\\titlerule \\vspace{-5pt}]\n\n"
        "\\pdfgentounicode=1\n\n"
        "\\newcommand{\\resumeItem}[1]{\n"
        "  \\item\\small{\n"
        "    {#1 \\vspace{-2pt}}\n"
        "  }\n"
        "}\n\n"
        "\\newcommand{\\resumeSubheading}[4]{\n"
        "  \\vspace{-2pt}\\item\n"
        "    \\begin{tabular*}{0.97\\textwidth}[t]{l@{\\extracolsep{\\fill}}r}\n"
        "      \\textbf{#1} & #2 \\\\\n"
        "      \\textit{\\small#3} & \\textit{\\small #4} \\\\\n"
        "    \\end{tabular*}\\vspace{-7pt}\n"
        "}\n\n"
        "\\newcommand{\\resumeSubSubheading}[2]{\n"
        "    \\item\n"
        "    \\begin{tabular*}{0.97\\textwidth}{l@{\\extracolsep{\\fill}}r}\n"
        "      \\textit{\\small#1} & \\textit{\\small #2} \\\\\n"
        "    \\end{tabular*}\\vspace{-7pt}\n"
        "}\n\n"
        "\\newcommand{\\resumeProjectHeading}[2]{\n"
        "    \\item\n"
        "    \\begin{tabular*}{0.97\\textwidth}{l@{\\extracolsep{\\fill}}r}\n"
        "      \\small#1 & #2 \\\\\n"
        "    \\end{tabular*}\\vspace{-7pt}\n"
        "}\n\n"
        "\\newcommand{\\resumeSubItem}[1]{\\resumeItem{#1}\\vspace{-4pt}}\n\n"
        "\\renewcommand\\labelitemii{$\\vcenter{\\hbox{\\tiny$\\bullet$}}$}\n\n"
        "\\newcommand{\\resumeSubHeadingListStart}{\\begin{itemize}[leftmargin=0.15in, label={}]}\n"
        "\\newcommand{\\resumeSubHeadingListEnd}{\\end{itemize}}\n"
        "\\newcommand{\\resumeItemListStart}{\\begin{itemize}}\n"
        "\\newcommand{\\resumeItemListEnd}{\\end{itemize}\\vspace{-5pt}}\n"
    )


    latex_template = (
        latex_preamble + 
        "\n"
        "\\begin{document}\n"

        # Header
        "\\begin{center}\n"
        "\\textbf{\\Huge \\scshape " + resume_data.profile.full_name + "} \\\\ \\vspace{1pt}\n"
        "\\small " + resume_data.profile.phone_no + " $|$ \\href{mailto:" + resume_data.profile.email + "}{" + "\\underline{" + resume_data.profile.email + "}} $|$ "
        + socials_str + "\n"
        "\\end{center}\n"

        # Education
        "\\section{Education}\n"
        "\\resumeSubHeadingListStart\n"
        + generate_education_section(resume_data.education) +
        "\\resumeSubHeadingListEnd\n"

        # Experience
        "\\section{Experience}\n"
        "\\resumeSubHeadingListStart\n"
        + generate_experience_section(resume_data.experience) +
        "\\resumeSubHeadingListEnd\n"

        # Projects
        "\\section{Projects}\n"
        "\\resumeSubHeadingListStart\n"
        + generate_project_section(resume_data.project) +
        "\\resumeSubHeadingListEnd\n"

        # Technical Skills
        "\\section{Technical Skills}\n"
        "\\begin{itemize}[leftmargin=0.15in, label={}]\n"
        "\\small{\\item{\n"
        "\\textbf{Languages}: " + ", ".join([lang.name for lang in resume_data.skills.tech_skills]) + " \\\\\n"
        "\\textbf{Frameworks}: " + ", ".join([fw.name for fw in resume_data.skills.frameworks]) + " \\\\\n"
        "\\textbf{Developer Tools}: " + ", ".join([tool.name for tool in resume_data.skills.developer_tools]) + " \\\\\n"
        "\\textbf{Libraries}: " + ", ".join([lib.name for lib in resume_data.skills.libraries]) + "\n"
        "}}\n"
        "\\end{itemize}\n"

        "\\end{document}\n"
    )
    return latex_template

def generate_education_section(education_list: List[Education]) -> str:
    return "\n".join([
        "   \\resumeSubheading{" + edu.name + "}{" + edu.start_year + " -- " + edu.end_year + "}{" + edu.degree + "}{" + edu.grade + "}"
        for edu in education_list
    ])

def generate_experience_section(experience_list: List[Experience]) -> str:
    experience_str = ""
    for exp in experience_list:
        experience_str += " \\resumeSubheading{" + exp.position + "}{" + exp.start_date + " -- " + exp.end_date + "}{" + exp.company_name + "}{"+ exp.location +"}\\resumeItemListStart\n"
        experience_str += "\n".join(["  \\resumeItem{" + desc.points + "}" for desc in exp.description])
        experience_str += " \\resumeItemListEnd\n"
    return experience_str

def generate_project_section(project_list: List[Project]) -> str:
    project_str = ""
    for proj in project_list:
        project_str += "    \\resumeProjectHeading{\\textbf{" + proj.name + "} $|$ \\emph{"+ proj.tech_stack +"}}{" + "\\href{" + proj.link_to_project + "}{" + "\\underline{Live}}}\n\\resumeItemListStart\n"
        project_str += "\n".join(["     \\resumeItem{" + desc.points + "}" for desc in proj.description])
        project_str += "    \\resumeItemListEnd\n"
    return project_str

def compile_latex_to_pdf(latex_code: str) -> str:
    # Save the LaTeX code to a .tex file
    with open("resume.tex", "w") as f:
        f.write(latex_code)

    # Compile the .tex file to a PDF
    try:
        subprocess.run(["pdflatex", "resume.tex"], check=True)
        return "resume.pdf"
    except subprocess.CalledProcessError:
        return None
