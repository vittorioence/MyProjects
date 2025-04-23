from setuptools import setup, find_packages

# Read README with proper encoding
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="consultai",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "langchain-community>=0.0.13",
        "faiss-cpu>=1.7.4",
        "sentence-transformers>=2.2.2"
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.12.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "types-python-dotenv>=1.0.0"
        ]
    },
    python_requires=">=3.8",
    author="Your Name",
    description="A medical ethics deliberation system using LLMs and RAG",
    long_description=long_description,
    long_description_content_type="text/markdown",
) 