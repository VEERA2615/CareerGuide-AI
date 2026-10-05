"""Career data. Add a career by adding one entry to CAREERS."""

CAREERS = {
    "Data Scientist": {
        "about": "Turn data into decisions with statistics and machine learning.",
        "skills": ["python", "sql", "pandas", "numpy", "statistics", "machine learning", "scikit-learn", "data visualization", "tensorflow"],
    },
    "Web Developer": {
        "about": "Build websites and web apps people use every day.",
        "skills": ["html", "css", "javascript", "react", "node.js", "git", "rest api", "sql", "typescript"],
    },
    "AI Engineer": {
        "about": "Ship products powered by language models and deep learning.",
        "skills": ["python", "machine learning", "deep learning", "pytorch", "llm", "prompt engineering", "fastapi", "docker", "git"],
    },
    "Backend Developer": {
        "about": "Design the servers, databases and APIs behind apps.",
        "skills": ["python", "java", "sql", "rest api", "fastapi", "docker", "git", "linux", "mongodb"],
    },
    "Data Analyst": {
        "about": "Find patterns in business data and explain them clearly.",
        "skills": ["excel", "sql", "python", "pandas", "power bi", "tableau", "statistics", "data visualization"],
    },
    "Cloud / DevOps Engineer": {
        "about": "Keep software deployed, fast and reliable.",
        "skills": ["linux", "docker", "kubernetes", "aws", "git", "ci/cd", "python", "networking"],
    },
}

# Extra spellings that count as the same skill.
ALIASES = {
    "javascript": ["js"], "node.js": ["nodejs", "node js"], "machine learning": ["ml"],
    "deep learning": ["neural network", "neural networks"], "llm": ["large language model", "llms", "langchain"],
    "rest api": ["restful", "rest apis", "api development"], "power bi": ["powerbi"],
    "scikit-learn": ["sklearn", "scikit learn"], "data visualization": ["matplotlib", "seaborn", "data visualisation"],
    "ci/cd": ["github actions", "jenkins"], "mongodb": ["mongo"], "aws": ["amazon web services"],
}

ALL_SKILLS = sorted({s for c in CAREERS.values() for s in c["skills"]} | {"c++", "c", "flask", "django", "mysql", "postgresql", "figma"})
